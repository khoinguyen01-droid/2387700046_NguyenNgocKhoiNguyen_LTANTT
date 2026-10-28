// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).

import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Lab 6 DevSecOps - Nguyen Ngoc Khoi Nguyen',
  tagline: 'Securing CI/CD Pipeline with GitLab',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  // 1. Cấu hình URL production chính xác cho GitLab Pages
  url: 'https://nguyenngockhoinguyen.gitlab.io',
  
  // 2. Cấu hình baseUrl khớp với tên repository của bạn trên GitLab
  baseUrl: '/lab06-nguyenngockhoinguyen/',

  // Cấu hình định danh cho GitLab
  organizationName: 'nguyenngockhoinguyen', 
  projectName: 'lab06-nguyenngockhoinguyen', 

  onBrokenLinks: 'throw',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl:
            'https://gitlab.com/nguyenngockhoinguyen/lab06-nguyenngockhoinguyen/-/tree/main/',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          editUrl:
            'https://gitlab.com/nguyenngockhoinguyen/lab06-nguyenngockhoinguyen/-/tree/main/',
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/docusaurus-social-card.jpg',
      colorMode: {
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'Lab 06 DevSecOps',
        logo: {
          alt: 'Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Tutorial',
          },
          {to: '/blog', label: 'Blog', position: 'left'},
          {
            href: 'https://gitlab.com/nguyenngockhoinguyen/lab06-nguyenngockhoinguyen',
            label: 'GitLab Repo',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Tutorial',
                to: '/docs/intro',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Blog',
                to: '/blog',
              },
              {
                label: 'GitLab',
                href: 'https://gitlab.com/nguyenngockhoinguyen/lab06-nguyenngockhoinguyen',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Nguyễn Ngọc Khôi Nguyên. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;