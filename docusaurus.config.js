// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).

import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Lab 6 DevSecOps - Nguyen Ngoc Khoi Nguyen',
  tagline: 'Securing CI/CD Pipeline with GitHub Pages',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  // 1. URL production của GitHub Pages
  url: 'https://khoinguyen01-droid.github.io',
  
  // 2. BaseUrl khớp chính xác với tên repository của bạn trên GitHub
  baseUrl: '/2387700046_NguyenNgocKhoiNguyen_LTANTT/',

  // Thông tin tài khoản và dự án trên GitHub
  organizationName: 'khoinguyen01-droid', 
  projectName: '2387700046_NguyenNgocKhoiNguyen_LTANTT', 

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
            'https://github.com/khoinguyen01-droid/2387700046_NguyenNgocKhoiNguyen_LTANTT/tree/main/',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          editUrl:
            'https://github.com/khoinguyen01-droid/2387700046_NguyenNgocKhoiNguyen_LTANTT/tree/main/',
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
            href: 'https://github.com/khoinguyen01-droid/2387700046_NguyenNgocKhoiNguyen_LTANTT',
            label: 'GitHub Repo',
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
                label: 'GitHub',
                href: 'https://github.com/khoinguyen01-droid/2387700046_NguyenNgocKhoiNguyen_LTANTT',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Nguyễn Ngọc Khôi Nguyên (2387700046). Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;