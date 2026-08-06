import type { StorybookConfig } from '@storybook/react-vite';

/**
 * Storybook di DOCUMENTAZIONE, non di componenti.
 *
 * Il DS Cross-App è mobile-native (CLAUDE.md R4): iOS, Android, iOS Liquid
 * Glass. Non esistono componenti web da renderizzare, e non devono esistere.
 * Quello che si pubblica qui è la documentazione dei 63 componenti, letta
 * dai metadata.json — cioè dall'unica fonte già allineata a Figma.
 *
 * Le storie sono generate: `npm run stories` le riscrive tutte da capo.
 */
const config: StorybookConfig = {
  stories: ['../storybook/generated/**/*.stories.tsx', '../storybook/*.stories.tsx'],
  addons: ['@storybook/addon-docs'],
  framework: '@storybook/react-vite',
  typescript: {
    // La documentazione non ha props da introspezionare: docgen è solo costo.
    reactDocgen: false,
  },
};

export default config;
