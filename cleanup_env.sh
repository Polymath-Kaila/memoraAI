#!/bin/bash
set -e  # stop on error

# 1️⃣ Check if in a Git repo
if [ ! -d ".git" ]; then
  echo "❌ Not a git repository. Run this in your project root."
  exit 1
fi

# 2️⃣ Ensure .env exists
if [ ! -f ".env" ]; then
  echo "⚠️  No .env file found. Continuing cleanup anyway..."
else
  echo "🗑️  Removing .env from working directory..."
  rm .env
fi

# 3️⃣ Add .env to .gitignore if not already there
if ! grep -qxF ".env" .gitignore 2>/dev/null; then
  echo ".env" >> .gitignore
  echo "🛡️  Added .env to .gitignore"
fi

git add .gitignore
git commit -m "chore: add .env to .gitignore" || echo "ℹ️  No changes to commit for .gitignore"

# 4️⃣ Ensure git-filter-repo is available
if ! command -v git-filter-repo &> /dev/null; then
  echo "🚧 Installing git-filter-repo via pip..."
  pip install git-filter-repo
fi

# 5️⃣ Remove .env from history
echo "🧹 Removing .env from Git history..."
git filter-repo --path .env --invert-paths --force

# 6️⃣ Force push cleaned history
echo "🚀 Force pushing cleaned repo to GitHub..."
git push origin --force --all
git push origin --force --tags

# 7️⃣ Done
echo "✅ Cleanup complete!"
echo "⚠️  Remember to rotate all secrets in your .env file immediately."
echo "💡 Tip: Add a .env.example with dummy values for future contributors."
