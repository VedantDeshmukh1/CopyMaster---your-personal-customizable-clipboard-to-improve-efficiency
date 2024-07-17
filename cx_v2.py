from cx_Freeze import setup, Executable

setup(

       name="CopyMaster",

       version="2.1",

       description="Helps copy things fast with UI",

       executables=[Executable("clipboard_monitor_v2.py")],

   )  