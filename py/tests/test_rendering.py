import os
import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from app import app, render_py_file

class TestPyFileRendering(unittest.TestCase):
    def setUp(self):
        """Set up test client and create a temporary directory for test files."""
        self.app = app.test_client()
        self.app.testing = True
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test files
        self.create_test_file('simple.py.html', """
            <p>2 + 2 = <?py= 2 + 2 ?></p>
            <p>Env var: <?py= os.getenv('TEST_VAR') ?></p>
        """)
        
        self.create_test_file('loops.py.html', """
            <ul>
            <?py for i in range(3): ?>
                <li>Item <?py= i ?></li>
            <?py # endfor ?>
            </ul>
        """)
        
        self.create_test_file('metadata.py.svg', """
            <?py
            metadata = {'api': {'url': 'http://test'}}
            ?>
            <svg>
                <script type="application/json" id="app-metadata">
                    <?py print(json.dumps(metadata)) ?>
                </script>
            </svg>
        """)
    
    def create_test_file(self, filename, content):
        """Helper to create test files."""
        path = os.path.join(self.temp_dir, filename)
        with open(path, 'w') as f:
            f.write(content.strip())
        return path
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)
    
    def test_simple_rendering(self):
        """Test basic Python expression rendering."""
        response = self.app.get('/simple.py.html')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<p>2 + 2 = 4</p>', response.data)
    
    def test_loop_rendering(self):
        """Test Python loops in templates."""
        response = self.app.get('/loops.py.html')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<li>0</li>', response.data)
        self.assertIn(b'<li>1</li>', response.data)
    
    def test_metadata_rendering(self):
        """Test metadata rendering in SVG files."""
        response = self.app.get('/metadata.py.svg')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'http://test', response.data)
    
    def test_file_not_found(self):
        """Test handling of non-existent files."""
        response = self.app.get('/nonexistent.py.html')
        self.assertEqual(response.status_code, 404)
    
    def test_invalid_extension(self):
        """Test that only .py.html and .py.svg files are processed."""
        response = self.app.get('/test.html')
        self.assertEqual(response.status_code, 404)
    
    def test_py_html_rendering(self):
        """Test that Python code in .py.html files is rendered correctly."""
        # Make a copy of the test file with a dynamic timestamp
        test_content = Path(self.test_file).read_text()
        test_content = test_content.replace("'TIME_PLACEHOLDER'", f"'{os.getenv('TEST_VAR')}'")
        Path(self.test_file).write_text(test_content)
        
        # Make a request to the test file
        with app.test_client() as client:
            response = client.get('/' + os.path.basename(self.test_file))
            
            # Check that the response is successful
            self.assertEqual(response.status_code, 200)
            
            # Check that the content type is HTML
            self.assertIn('text/html', response.content_type)
            
            # Check that Python code was executed
            self.assertIn(b'2 + 2 = 4', response.data)
            self.assertIn(b'<li>Item 0</li>', response.data)
            self.assertIn(b'<li>Item 1</li>', response.data)
            self.assertIn(b'<li>Item 2</li>', response.data)
            
            # Check that environment variables are accessible
            self.assertIn(b'test_value', response.data)
    
    def test_index_rendering(self):
        """Test that the index page renders correctly."""
        # Create a temporary index.py.html
        index_file = os.path.join(self.temp_dir, 'index.py.html')
        with open(index_file, 'w') as f:
            f.write("<h1>Test Index</h1>")
        
        # Temporarily change the index route to use our test file
        original_index = app.view_functions['index']
        
        def test_index():
            return app.send_static_file('index.py.html')
        
        app.view_functions['index'] = test_index
        
        try:
            with app.test_client() as client:
                response = client.get('/')
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Test Index', response.data)
        finally:
            # Restore the original index route
            app.view_functions['index'] = original_index

if __name__ == '__main__':
    unittest.main()
