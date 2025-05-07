Setup Instructions (Windows)
1. Clone the Repository and Initialize Submodules

After cloning the repository, run the following command to pull in Defects4J as a submodule:

`git submodule update --init --recursive`

2. Set Up Java 8 (JDK 1.8)
Step 1: Install JDK 8

    Download JDK 8 from a trusted source such as Eclipse Temurin (formerly AdoptOpenJDK).

    Install the JDK and take note of the installation directory. Example:
    C:\Program Files\Eclipse Adoptium\jdk-8.0.XXX-hotspot

Step 2: Set Environment Variables

Open the Environment Variables dialog:

    Press the Windows key, type environment variables, and select Edit the system environment variables.

    In the System Properties dialog, click Environment Variables....

Set the following system environment variables:

JAVA_HOME

    Click New under System variables.

    Variable name: JAVA_HOME

    Variable value: your JDK path (e.g. C:\Program Files\Eclipse Adoptium\jdk-8.0.XXX-hotspot)

Path

    Select the Path variable under System variables and click Edit....

    Click New and add:
    %JAVA_HOME%\bin

CLASSPATH (optional but recommended for Defects4J)

    Click New under System variables.

    Variable name: CLASSPATH

    Variable value:
    .;%JAVA_HOME%\lib\dt.jar;%JAVA_HOME%\lib\tools.jar

Click OK to close all dialogs and apply the changes.

3. Add Defects4J to System PATH

Assuming the repository was cloned to C:\Users\YourUsername\YourRepo, and Defects4J is in the external/defects4j subdirectory:

    Go to Environment Variables.

    Edit the Path variable under System variables.

    Click New and add:

C:\Users\YourUsername\YourRepo\external\defects4j\framework\bin

(Replace the path with your actual local path to the defects4j/framework/bin directory.)

4. Verify the Setup

Open a new Command Prompt and run:

`java -version`

Expected output:

`java version "1.8.0_XXX"`
`Java(TM) SE Runtime Environment (build 1.8.0_XXX)`

Also run:

`defects4j help`

You should see Defects4J's help text output, confirming the setup was successful.

5. Set Up Python - Required for BugsInPy
Install Python: Ensure you have Python 3.x installed. You can download it from python.org.
Add Python to PATH: Make sure Python and Pip are added to your system's PATH environment variable during installation or manually afterwards.
    Typically, Python installers for Windows have an option "Add Python to PATH".
    You can verify by opening a new terminal and typing python --version and pip --version.

6. Add BugsInPy to System PATH

Assuming this repository was cloned to C:\YourRepo and BugsInPy is in the C:\YourRepo\external\bugsinpy subdirectory:

    Go back to Environment Variables.
    Select the Path variable under System variables and click Edit....
    Click New and add the absolute path to the framework/bin directory of BugsInPy:
        Example: C:\YourRepo\external\bugsinpy\framework\bin (Replace C:\YourRepo with the actual local path to your repository.)

Click OK on all dialogs to apply the changes.

7. Verify

python --version

Expected output should show Python 3.x.x.

bugsinpy-checkout --help

You should see BugsInPy's help text for the checkout command, confirming it's accessible.