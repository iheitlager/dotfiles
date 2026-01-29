-- Copyright 2026 Ilja Heitlager
-- SPDX-License-Identifier: Apache-2.0

-- Neovim configuration
-- Inherits vim config and adds modern features

-- Load vim config for shared settings
local vim_config = vim.fn.expand('$XDG_CONFIG_HOME/vim/vimrc')
if vim.fn.filereadable(vim_config) == 1 then
  vim.cmd('source ' .. vim_config)
end

-- Modern Neovim-specific settings
vim.opt.termguicolors = true      -- True color support
vim.opt.signcolumn = 'yes'        -- Always show sign column
vim.opt.updatetime = 250          -- Faster completion
vim.opt.timeoutlen = 300          -- Faster key sequence completion
vim.opt.splitbelow = true         -- Horizontal splits below
vim.opt.splitright = true         -- Vertical splits to the right
vim.opt.cursorline = true         -- Highlight current line
vim.opt.scrolloff = 8             -- Keep 8 lines above/below cursor
vim.opt.sidescrolloff = 8         -- Keep 8 columns left/right of cursor

-- Better search
vim.opt.inccommand = 'split'      -- Preview substitutions

-- Disable mouse (optional, uncomment if you prefer)
-- vim.opt.mouse = ''

-- Use system clipboard
vim.opt.clipboard = 'unnamedplus'

-- Line numbers
vim.opt.relativenumber = true     -- Relative line numbers
vim.opt.number = true             -- Show current line number

-- Leader key (space is popular)
vim.g.mapleader = ' '
vim.g.maplocalleader = ' '

-- Key mappings
local keymap = vim.keymap.set
local opts = { noremap = true, silent = true }

-- Better window navigation
keymap('n', '<C-h>', '<C-w>h', opts)
keymap('n', '<C-j>', '<C-w>j', opts)
keymap('n', '<C-k>', '<C-w>k', opts)
keymap('n', '<C-l>', '<C-w>l', opts)

-- Clear search highlighting with Escape
keymap('n', '<Esc>', '<cmd>nohlsearch<CR>', opts)

-- Better indenting (stay in visual mode)
keymap('v', '<', '<gv', opts)
keymap('v', '>', '>gv', opts)

-- Move lines up/down
keymap('v', 'J', ":m '>+1<CR>gv=gv", opts)
keymap('v', 'K', ":m '<-2<CR>gv=gv", opts)

-- Keep cursor centered when scrolling
keymap('n', '<C-d>', '<C-d>zz', opts)
keymap('n', '<C-u>', '<C-u>zz', opts)
keymap('n', 'n', 'nzzzv', opts)
keymap('n', 'N', 'Nzzzv', opts)

-- Quick save
keymap('n', '<leader>w', '<cmd>w<CR>', opts)

-- Quick quit
keymap('n', '<leader>q', '<cmd>q<CR>', opts)

-- Buffer navigation
keymap('n', '<S-h>', '<cmd>bprevious<CR>', opts)
keymap('n', '<S-l>', '<cmd>bnext<CR>', opts)

-- Diagnostics
keymap('n', '[d', vim.diagnostic.goto_prev, { desc = 'Go to previous diagnostic' })
keymap('n', ']d', vim.diagnostic.goto_next, { desc = 'Go to next diagnostic' })
keymap('n', '<leader>e', vim.diagnostic.open_float, { desc = 'Show diagnostic error' })

-- File explorer (netrw)
keymap('n', '<leader>pv', vim.cmd.Ex, { desc = 'Open file explorer' })

-- Highlight on yank
vim.api.nvim_create_autocmd('TextYankPost', {
  group = vim.api.nvim_create_augroup('highlight_yank', { clear = true }),
  callback = function()
    vim.highlight.on_yank({ timeout = 200 })
  end,
})

-- Bootstrap lazy.nvim plugin manager
local lazypath = vim.fn.stdpath('data') .. '/lazy/lazy.nvim'
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    'git', 'clone', '--filter=blob:none',
    'https://github.com/folke/lazy.nvim.git',
    '--branch=stable', lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

-- Plugins
require('lazy').setup({
  -- Colorscheme
  {
    'folke/tokyonight.nvim',
    lazy = false,
    priority = 1000,
    config = function()
      vim.cmd.colorscheme('tokyonight-night')
    end,
  },

  -- Fuzzy finder
  {
    'nvim-telescope/telescope.nvim',
    branch = '0.1.x',
    dependencies = { 'nvim-lua/plenary.nvim' },
    keys = {
      { '<leader>ff', '<cmd>Telescope find_files<CR>', desc = 'Find files' },
      { '<leader>fg', '<cmd>Telescope live_grep<CR>', desc = 'Live grep' },
      { '<leader>fb', '<cmd>Telescope buffers<CR>', desc = 'Buffers' },
      { '<leader>fh', '<cmd>Telescope help_tags<CR>', desc = 'Help tags' },
      { '<leader><leader>', '<cmd>Telescope buffers<CR>', desc = 'Buffers' },
    },
  },

  -- Treesitter for better syntax highlighting
  {
    'nvim-treesitter/nvim-treesitter',
    build = ':TSUpdate',
    config = function()
      -- API changed: 'configs' -> 'config' in newer versions
      require('nvim-treesitter.config').setup({
        ensure_installed = { 'lua', 'vim', 'vimdoc', 'bash', 'python', 'javascript', 'typescript', 'json', 'yaml', 'markdown' },
        auto_install = true,
        highlight = { enable = true },
        indent = { enable = true },
      })
    end,
  },

  -- Git signs in gutter
  {
    'lewis6991/gitsigns.nvim',
    config = function()
      require('gitsigns').setup()
    end,
  },

  -- Status line
  {
    'nvim-lualine/lualine.nvim',
    dependencies = { 'nvim-tree/nvim-web-devicons' },
    config = function()
      require('lualine').setup({
        options = { theme = 'tokyonight' },
      })
    end,
  },

  -- Surround (like vim-surround)
  { 'kylechui/nvim-surround', event = 'VeryLazy', config = true },

  -- Comment toggling
  { 'numToStr/Comment.nvim', config = true },

  -- Autopairs
  { 'windwp/nvim-autopairs', event = 'InsertEnter', config = true },

  -- Which-key (shows keybindings)
  {
    'folke/which-key.nvim',
    event = 'VeryLazy',
    config = function()
      require('which-key').setup()
    end,
  },

  -- Git integration
  { 'tpope/vim-fugitive' },

}, {
  -- lazy.nvim options
  checker = { enabled = false },  -- Don't auto-check for updates
})
