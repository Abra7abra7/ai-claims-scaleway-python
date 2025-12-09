#!/usr/bin/env node
/**
 * Pre-commit hook for auto-generating TypeScript types
 * 
 * This script:
 * 1. Checks if backend is running
 * 2. Generates TypeScript types from OpenAPI
 * 3. Stages the generated types file
 */

const { execSync } = require('child_process');
const http = require('http');

console.log('🔄 Pre-commit: Checking for TypeScript types updates...');

// Check if backend is running
function checkBackend() {
  return new Promise((resolve) => {
    const req = http.get('http://localhost:8000/api/v1/health', (res) => {
      resolve(res.statusCode === 200);
    });
    
    req.on('error', () => {
      resolve(false);
    });
    
    req.setTimeout(2000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

async function main() {
  const backendRunning = await checkBackend();
  
  if (!backendRunning) {
    console.log('⚠️  Backend is not running on localhost:8000');
    console.log('💡 Tip: Start backend with: docker compose up -d backend');
    console.log('⏭️  Skipping type generation (using existing types)');
    process.exit(0);
  }
  
  console.log('✅ Backend is running');
  console.log('🔄 Generating TypeScript types...');
  
  try {
    // Generate types
    execSync('cd frontend && npm run generate-types', {
      stdio: 'inherit',
      encoding: 'utf-8'
    });
    
    // Check if types file changed
    try {
      const gitDiff = execSync('git diff --name-only frontend/src/lib/api-types.ts', {
        encoding: 'utf-8'
      }).trim();
      
      if (gitDiff) {
        console.log('📝 Types updated - staging changes...');
        execSync('git add frontend/src/lib/api-types.ts', { stdio: 'inherit' });
        console.log('✅ TypeScript types generated and staged');
      } else {
        console.log('✅ Types are up to date');
      }
    } catch (e) {
      // No changes or file doesn't exist yet
      console.log('✅ Types generated');
    }
    
    process.exit(0);
  } catch (error) {
    console.error('❌ Failed to generate types:', error.message);
    console.log('⏭️  Proceeding with commit (using existing types)');
    process.exit(0); // Don't block commit
  }
}

main();

