import type { Preview } from '@storybook/react-vite';

const preview: Preview = {
  parameters: {
    layout: 'fullscreen',
    controls: { disable: true },
    actions: { disable: true },
    options: {
      // Niente componenti interattivi da ispezionare: il pannello degli addon
      // resterebbe vuoto occupando meta' schermo.
      showPanel: false,
      // Ordine della sidebar: prima l'overview, poi i componenti per categoria.
      storySort: {
        order: ['Panoramica', 'Componenti'],
      },
    },
  },
};

export default preview;
