from parsing import ASTParser
import json

parser = ASTParser()

result = parser.parse_file("example.java")  

print(json.dumps(result, indent=4, default=str))