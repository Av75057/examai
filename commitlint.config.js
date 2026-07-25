module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'scope-enum': [2, 'always', [
      'backend', 'frontend', 'bot', 'infra', 'docs',
      'admin', 'exam', 'ai', 'deps'
    ]],
  },
};
