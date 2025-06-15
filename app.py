import os
import tempfile
import subprocess
import logging
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_script(script):
    """Validating the script for security constraints like checking if main is there or if it is empty"""
    if not script.strip():
        raise ValueError("Empty script")
    
    forbidden_patterns = [
        "__import__", "open(", "eval(", "exec(", 
        "os.system", "subprocess", "import os",
        "import subprocess"
    ]
    
    for pattern in forbidden_patterns:
        if pattern in script:
            raise ValueError(f"Forbidden pattern detected: {pattern}")
    
    if 'def main():' not in script:
        raise ValueError("Script must contain a main() function")

def execute_safely(script):
    """Executing the script in nsjail sandbox for the question"""
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', dir='/sandbox', delete=False) as f:
        script_path = f.name
        f.write(script)
        f.write('\n\nif __name__ == "__main__":\n')
        f.write('    import json, sys\n')
        f.write('    from io import StringIO\n')
        f.write('    original_stdout = sys.stdout\n')
        f.write('    sys.stdout = captured_stdout = StringIO()\n')
        f.write('    try:\n')
        f.write('        result = main()\n')
        f.write('        json_result = json.dumps({"result": result})\n')
        f.write('    except Exception as e:\n')
        f.write('        json_result = json.dumps({"error": str(e)})\n')
        f.write('    finally:\n')
        f.write('        sys.stdout = original_stdout\n')
        f.write('    print(json_result)\n')
        f.write('    print(captured_stdout.getvalue(), end="")\n')
    
    try:
        cmd = [
            'nsjail',
            '--config', '/etc/nsjail/nsjail.cfg',
            '--',
            '/usr/local/bin/python3', script_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Execution failed: {result.stderr}")

        # Split output into JSON result and captured stdout
        output_lines = result.stdout.strip().split('\n')
        if not output_lines:
            raise RuntimeError("No output received from script")

        try:
            json_output = json.loads(output_lines[0])
        except json.JSONDecodeError:
            raise RuntimeError(f"Invalid JSON format: {output_lines[0]}")

        stdout_content = '\n'.join(output_lines[1:]) if len(output_lines) > 1 else ''
        
        if 'error' in json_output:
            raise ValueError(json_output['error'])

        return {
            'result': json_output.get('result'),
            'stdout': stdout_content
        }
            
    finally:
        try:
            os.unlink(script_path)
        except:
            pass

@app.route('/execute', methods=['POST'])
def execute():
    try:
        data = request.get_json()
        if not data or 'script' not in data:
            return jsonify({"error": "Missing script"}), 400
            
        script = data['script']
        validate_script(script)
        result = execute_safely(script)
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Execution error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)