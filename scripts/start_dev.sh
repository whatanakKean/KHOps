"""Development startup script"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start development environment"""

    print("🚀 Starting KHOps Development Environment\n")

    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Check if .env exists, if not copy from .env.example
    if not Path(".env").exists():
        print("📝 Creating .env from .env.example...")
        with open(".env.example") as src, open(".env", "w") as dst:
            dst.write(src.read())

    # Start Docker services
    print("\n🐳 Starting Docker services...")
    subprocess.run(["docker-compose", "-f", "docker/docker-compose.yml", "up", "-d"])

    print("\n✅ Development environment started!")
    print("\n📚 Useful commands:")
    print("   make server       - Start API server")
    print("   make test         - Run tests")
    print("   make lint         - Run linting")
    print("   make docker-logs  - View Docker logs")
    print("\n🌐 Access points:")
    print("   API:       http://localhost:8000")
    print("   Docs:      http://localhost:8000/docs")
    print("   Grafana:   http://localhost:3000")
    print("   Prometheus: http://localhost:9090")

if __name__ == "__main__":
    main()
