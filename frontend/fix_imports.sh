#!/bin/bash

# Remove getAuthHeaders imports
find src -name "*.tsx" -type f -exec sed -i '/getAuthHeaders/d' {} \;

# Replace apiRequest imports
find src -name "*.tsx" -type f -exec sed -i 's/apiRequest/api/g' {} \;

# Add api import where needed
for file in $(find src -name "*.tsx" -type f); do
  if grep -q "api\." "$file" && ! grep -q "import.*api.*from.*@/lib/api" "$file"; then
    sed -i '1a import { api } from "@/lib/api";' "$file"
  fi
done

echo "Fixed imports in all TSX files"
