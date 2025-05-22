# Copyright (c) 2014, Chris Church <chris@ninemoreminutes.com>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

DOCUMENTATION = """
name: powershell
version_added: historical
short_description: Windows PowerShell
description:
- The only option when using 'winrm' or 'psrp' as a connection plugin.
- Can also be used when using 'ssh' as a connection plugin and the C(DefaultShell) has been configured to PowerShell.
extends_documentation_fragment:
- shell_windows
"""

import base64
import os
import re
import shlex
import xml.etree.ElementTree as ET
import ntpath

from ansible.executor.powershell.module_manifest import _bootstrap_powershell_script, _get_powershell_script
from ansible.module_utils.common.text.converters import to_bytes, to_text
from ansible.plugins.shell import ShellBase, _ShellCommand

# This is weird, we are matching on byte sequences that match the utf-16-be
# matches for '_x(a-fA-F0-9){4}_'. The \x00 and {4} will match the hex sequence
# when it is encoded as utf-16-be byte sequence.
_STRING_DESERIAL_FIND = re.compile(rb"\x00_\x00x((?:\x00[a-fA-F0-9]){4})\x00_")

_common_args = ['PowerShell', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Unrestricted']


def _replace_stderr_clixml(stderr: bytes) -> bytes:
    """Detect and decode CLIXML errors in PowerShell output."""
    if b"#< CLIXML" not in stderr:
        return stderr

    processed = []
    buffer = []
    in_clixml = False

    for line in stderr.splitlines(True):
        if line == b"#< CLIXML\r\n":
            in_clixml = True
            buffer = []
        elif in_clixml and b"</Objs>" in line:
            buffer.append(line)
            processed.append(_parse_clixml(b"".join(buffer)))
            in_clixml = False
        elif in_clixml:
            buffer.append(line)
        else:
            processed.append(line)

    return b"".join(processed)

def _parse_clixml(data: bytes, stream: str = "Error") -> bytes:
    """Extract error messages from PowerShell CLIXML data."""
    lines: list[str] = []
    while data:
        start_idx = data.find(b"<Objs ")
        end_idx = data.find(b"</Objs>")
        if start_idx == -1 or end_idx == -1:
            break

        current_element = data[start_idx:end_idx+7]
        data = data[end_idx+7:]

        try:
            clixml = ET.fromstring(current_element)
            namespace = "{" + clixml.tag.split("}")[0][1:] + "}" if "}" in clixml.tag else ""
            for string_entry in clixml.findall(f"./{namespace}S"):
                if string_entry.attrib.get('S') == stream:
                    b_line = string_entry.text.encode("utf-16-be")
                    b_escaped = re.sub(_STRING_DESERIAL_FIND, lambda m: base64.b16decode(m.group(1).decode("utf-16-be").upper()), b_line)
                    lines.append(b_escaped.decode("utf-16-be"))
        except Exception:
            continue

    return to_bytes("".join(lines), errors="surrogatepass")

class ShellModule(ShellBase):

    # Common shell filenames that this plugin handles
    # Powershell is handled differently.  It's selected when winrm is the
    # connection
    COMPATIBLE_SHELLS = frozenset()  # type: frozenset[str]
    # Family of shells this has.  Must match the filename without extension
    SHELL_FAMILY = 'powershell'

    # We try catch as some connection plugins don't have a console (PSRP).
    _CONSOLE_ENCODING = "try { [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding } catch {}"
    _SHELL_REDIRECT_ALLNULL = '> $null'
    _SHELL_AND = ';'

    # Used by various parts of Ansible to do Windows specific changes
    _IS_WINDOWS = True

    # TODO: add binary module support

    def env_prefix(self, **kwargs):
        # powershell/winrm env handling is handled in the exec wrapper
        return ""

    def join_path(self, *args):
        # use normpath() to remove doubled slashed and convert forward to backslashes
        parts = [ntpath.normpath(self._unquote(arg)) for arg in args]

        # Because ntpath.join treats any component that begins with a backslash as an absolute path,
        # we have to strip slashes from at least the beginning, otherwise join will ignore all previous
        # path components except for the drive.
        return ntpath.join(parts[0], *[part.strip('\\') for part in parts[1:]])

    def get_remote_filename(self, pathname):
        # powershell requires that script files end with .ps1
        base_name = os.path.basename(pathname.strip())
        name, ext = os.path.splitext(base_name.strip())
        if ext.lower() not in ['.ps1', '.exe']:
            return name + '.ps1'

        return base_name.strip()

    def path_has_trailing_slash(self, path):
        # Allow Windows paths to be specified using either slash.
        path = self._unquote(path)
        return path.endswith('/') or path.endswith('\\')

    def chmod(self, paths, mode):
        raise NotImplementedError('chmod is not implemented for Powershell')

    def chown(self, paths, user):
        raise NotImplementedError('chown is not implemented for Powershell')

    def set_user_facl(self, paths, user, mode):
        raise NotImplementedError('set_user_facl is not implemented for Powershell')

    def remove(self, path, recurse=False):
        path = self._escape(self._unquote(path))
        if recurse:
            return self._encode_script("""Remove-Item '%s' -Force -Recurse;""" % path)
        else:
            return self._encode_script("""Remove-Item '%s' -Force;""" % path)

    def mkdtemp(
        self,
        basefile: str | None = None,
        system: bool = False,
        mode: int = 0o700,
        tmpdir: str | None = None,
    ) -> str:
        # This is not called in Ansible anymore but it is kept for backwards
        # compatibility in case other action plugins outside Ansible calls this.
        if not basefile:
            basefile = self.__class__._generate_temp_dir_name()
        basefile = self._escape(self._unquote(basefile))
        basetmpdir = self._escape(tmpdir if tmpdir else self.get_option('remote_tmp'))

        script = f"""
        {self._CONSOLE_ENCODING}
        $tmp_path = [System.Environment]::ExpandEnvironmentVariables('{basetmpdir}')
        $tmp = New-Item -Type Directory -Path $tmp_path -Name '{basefile}'
        Write-Output -InputObject $tmp.FullName
        """
        return self._encode_script(script.strip())

    def _mkdtemp2(
        self,
        basefile: str | None = None,
        system: bool = False,
        mode: int = 0o700,
        tmpdir: str | None = None,
    ) -> _ShellCommand:
        # Windows does not have an equivalent for the system temp files, so
        # the param is ignored
        if not basefile:
            basefile = self.__class__._generate_temp_dir_name()

        basefile = self._unquote(basefile)
        basetmpdir = tmpdir if tmpdir else self.get_option('remote_tmp')

        script, stdin = _bootstrap_powershell_script("powershell_mkdtemp.ps1", {
            'Directory': basetmpdir,
            'Name': basefile,
        })

        return _ShellCommand(
            command=self._encode_script(script),
            input_data=stdin,
        )

    def expand_user(
        self,
        user_home_path: str,
        username: str = '',
    ) -> str:
        # This is not called in Ansible anymore but it is kept for backwards
        # compatibility in case other actions plugins outside Ansible called this.
        user_home_path = self._unquote(user_home_path)
        if user_home_path == '~':
            script = 'Write-Output (Get-Location).Path'
        elif user_home_path.startswith('~\\'):
            script = "Write-Output ((Get-Location).Path + '%s')" % self._escape(user_home_path[1:])
        else:
            script = "Write-Output '%s'" % self._escape(user_home_path)
        return self._encode_script(f"{self._CONSOLE_ENCODING}; {script}")

    def _expand_user2(
        self,
        user_home_path: str,
        username: str = '',
    ) -> _ShellCommand:
        user_home_path = self._unquote(user_home_path)
        script, stdin = _bootstrap_powershell_script("powershell_expand_user.ps1", {
            'Path': user_home_path,
        })

        return _ShellCommand(
            command=self._encode_script(script),
            input_data=stdin,
        )

    def exists(self, path):
        path = self._escape(self._unquote(path))
        script = """
            If (Test-Path '%s')
            {
                $res = 0;
            }
            Else
            {
                $res = 1;
            }
            Write-Output '$res';
            Exit $res;
         """ % path
        return self._encode_script(script)

    def checksum(self, path, *args, **kwargs):
        path = self._escape(self._unquote(path))
        script = """
            If (Test-Path -PathType Leaf '%(path)s')
            {
                $sp = new-object -TypeName System.Security.Cryptography.SHA1CryptoServiceProvider;
                $fp = [System.IO.File]::Open('%(path)s', [System.IO.Filemode]::Open, [System.IO.FileAccess]::Read);
                [System.BitConverter]::ToString($sp.ComputeHash($fp)).Replace("-", "").ToLower();
                $fp.Dispose();
            }
            ElseIf (Test-Path -PathType Container '%(path)s')
            {
                Write-Output "3";
            }
            Else
            {
                Write-Output "1";
            }
        """ % dict(path=path)
        return self._encode_script(script)

    def build_module_command(self, env_string, shebang, cmd, arg_path=None):
        bootstrap_wrapper = _get_powershell_script("bootstrap_wrapper.ps1")

        # pipelining bypass
        if cmd == '':
            return self._encode_script(script=bootstrap_wrapper, strict_mode=False, preserve_rc=False)

        # non-pipelining

        cmd_parts = shlex.split(cmd, posix=False)
        cmd_parts = list(map(to_text, cmd_parts))
        if shebang and shebang.lower() == '#!powershell':
            if arg_path:
                # Running a module without the exec_wrapper and with an argument
                # file.
                script_path = self._unquote(cmd_parts[0])
                if not script_path.lower().endswith('.ps1'):
                    script_path += '.ps1'

                cmd_parts.insert(0, '-File')
                cmd_parts[1] = f'"{script_path}"'
                if arg_path:
                    cmd_parts.append(f'"{arg_path}"')

                wrapper_cmd = " ".join(_common_args + cmd_parts)
                return wrapper_cmd

            else:
                # Running a module with ANSIBLE_KEEP_REMOTE_FILES=true, the script
                # arg is actually the input manifest JSON to provide to the bootstrap
                # wrapper.
                wrapper_cmd = "type " + cmd_parts[0] + " | " + self._encode_script(script=bootstrap_wrapper, strict_mode=False, preserve_rc=False)
                return wrapper_cmd

        elif shebang and shebang.startswith('#!'):
            cmd_parts.insert(0, shebang[2:])
        elif not shebang:
            # The module is assumed to be a binary
            cmd_parts[0] = self._unquote(cmd_parts[0])
            cmd_parts.append(arg_path)
        script = """
            Try
            {
                %s
                %s
            }
            Catch
            {
                $stderr = $_ | Out-String -Stream
                $stderr = [System.Text.Encoding]::UTF8.GetBytes($stderr)
                $decoded_stderr = [System.Text.Encoding]::UTF8.GetString(
                    (Ansible.Utils.PowerShell._replace_stderr_clixml($stderr))
                $_obj = @{ failed = $true }
                If ($_.Exception.GetType)
                {
                    $_obj.Add('msg', $_.Exception.Message)
                }
                Else
                {
                    $_obj.Add('msg', $_.ToString())
                }
                If ($_.InvocationInfo.PositionMessage)
                {
                    $_obj.Add('exception', $_.InvocationInfo.PositionMessage)
                }
                ElseIf ($_.ScriptStackTrace)
                {
                    $_obj.Add('exception', $_.ScriptStackTrace)
                }
                Try
                {
                    $_obj.Add('error_record', ($_ | ConvertTo-Json | ConvertFrom-Json))
                }
                Catch
                {
                }
                Echo $_obj | ConvertTo-Json -Compress -Depth 99
                Exit 1
            }
        """ % (env_string, ' '.join(cmd_parts))
        return self._encode_script(script, preserve_rc=False)

    def wrap_for_exec(self, cmd):
        return '& %s; exit $LASTEXITCODE' % cmd

    def _unquote(self, value):
        """Remove any matching quotes that wrap the given value."""
        value = to_text(value or '')
        m = re.match(r'^\s*?\'(.*?)\'\s*?$', value)
        if m:
            return m.group(1)
        m = re.match(r'^\s*?"(.*?)"\s*?$', value)
        if m:
            return m.group(1)
        return value

    def _escape(self, value):
        """Return value escaped for use in PowerShell single quotes."""
        # There are 5 chars that need to be escaped in a single quote.
        # https://github.com/PowerShell/PowerShell/blob/b7cb335f03fe2992d0cbd61699de9d9aafa1d7c1/src/System.Management.Automation/engine/parser/CharTraits.cs#L265-L272
        return re.compile(u"(['\u2018\u2019\u201a\u201b])").sub(u'\\1\\1', value)

    def _encode_script(self, script, as_list=False, strict_mode=True, preserve_rc=True):
        """Convert a PowerShell script to a single base64-encoded command."""
        script = to_text(script)

        if script == u'-':
            cmd_parts = _common_args + ['-Command', '-']

        else:
            if strict_mode:
                script = u'Set-StrictMode -Version Latest\r\n%s' % script
            # try to propagate exit code if present- won't work with begin/process/end-style scripts (ala put_file)
            # NB: the exit code returned may be incorrect in the case of a successful command followed by an invalid command
            if preserve_rc:
                script = u'%s\r\nIf (-not $?) { If (Get-Variable LASTEXITCODE -ErrorAction SilentlyContinue) { exit $LASTEXITCODE } Else { exit 1 } }\r\n'\
                    % script
            script = '\n'.join([x.strip() for x in script.splitlines() if x.strip()])
            encoded_script = to_text(base64.b64encode(script.encode('utf-16-le')), 'utf-8')
            cmd_parts = _common_args + ['-EncodedCommand', encoded_script]

        if as_list:
            return cmd_parts
        return ' '.join(cmd_parts)
