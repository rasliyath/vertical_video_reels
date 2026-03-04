#!/usr/bin/env bash
# reels-backend/build.sh

set -e  # stop on any error

echo "⬆️ Upgrading pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel

echo "📦 Installing requirements..."
pip install -r requirements.txt

echo "✅ Build complete!"