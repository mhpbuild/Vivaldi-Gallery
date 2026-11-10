import parser from '@typescript-eslint/parser';
import tsPlugin from '@typescript-eslint/eslint-plugin';
export default [{
  files: ['src/**/*.{ts,tsx}'],
  languageOptions: { parser, ecmaVersion: 'latest', sourceType: 'module' },
  plugins: { '@typescript-eslint': tsPlugin },
  rules: {
    '@typescript-eslint/no-unused-vars': 'error',
    'no-debugger': 'error',
    'no-duplicate-imports': ['error', { allowSeparateTypeImports: true }],
    'no-constant-condition': 'error',
    'no-unreachable': 'error',
    'no-var': 'error',
    'eqeqeq': 'error'
  }
}];
