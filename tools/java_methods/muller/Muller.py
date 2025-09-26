import jpype
import json
import os
import sys

def start_jvm():
    """Start JVM with proper classpath"""
    if not jpype.isJVMStarted():
        # Get the absolute path to the muller directory
        if hasattr(sys, '_MEIPASS'):  # If running from PyInstaller
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        muller_dir = os.path.join(base_path, "tools", "java_methods", "muller")
        
        print(f"Looking for Java classes in: {muller_dir}")
        print(f"Files in directory: {os.listdir(muller_dir) if os.path.exists(muller_dir) else 'Directory not found'}")
        
        # Start JVM with classpath
        jpype.startJVM(jpype.getDefaultJVMPath(), f"-Djava.class.path={muller_dir}")

def muller_method(function: str, p0: float, p1: float, p2: float, nmax: int, last_n_rows: int, tolerance: float):
    """
    Python interface for Muller's method implemented in Java
    """
    
    # Start JVM if not already started
    start_jvm()
    
    try:
        # Try different ways to access the class
        try:
            # First try: Simple class name
            MullerClass = jpype.JClass("Muller")
        except:
            try:
                # Second try: Add current directory to classpath
                current_dir = os.getcwd()
                muller_path = os.path.join(current_dir, "tools", "java_methods", "muller")
                jpype.addClassPath(muller_path)
                MullerClass = jpype.JClass("Muller")
            except:
                # Third try: Direct file path approach
                import subprocess
                result = subprocess.run([
                    'java', '-cp', 'tools/java_methods/muller', 'Muller', 
                    function, str(p0), str(p1), str(p2), str(nmax), str(last_n_rows), str(tolerance)
                ], capture_output=True, text=True, cwd=os.getcwd())
                
                if result.returncode == 0:
                    return json.loads(result.stdout)
                else:
                    raise Exception(f"Java execution failed: {result.stderr}")
        
        # Call Java method which returns JSON string
        json_result = MullerClass.mullerController(function, float(p0), float(p1), float(p2), 
                                                  int(nmax), int(last_n_rows), float(tolerance))
        
        # Parse JSON string to Python dictionary
        python_result = json.loads(str(json_result))
        
        return python_result
        
    except Exception as e:
        print(f"Error calling Java method: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python file location: {__file__}")
        
        return {
            "iterations": [],
            "roots": [],
            "errors": [],
            "final_root": "Error",
            "message": f"Error: {str(e)}"
        }

def muller_controller(function: str, p0: float, p1: float, p2: float, nmax: int, last_n_rows: int, tolerance: float):
    """Controller function to match the bisection pattern"""
    return muller_method(function, p0, p1, p2, nmax, last_n_rows, tolerance)