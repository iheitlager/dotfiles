-- Copyright 2026 Ilja Heitlager
-- SPDX-License-Identifier: Apache-2.0

-- Neovim configuration
-- Inherits vim config and adds modern features

-- Load vim config for shared settings
-- @diagnostic disable: undefined-global
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

-- YAML-specific settings
vim.api.nvim_create_autocmd('FileType', {
  pattern = 'yaml',
  group = vim.api.nvim_create_augroup('yaml_settings', { clear = true }),
  callback = function()
    -- Better indentation for YAML
    vim.opt_local.shiftwidth = 2
    vim.opt_local.tabstop = 2
    vim.opt_local.softtabstop = 2
    vim.opt_local.expandtab = true

    -- Show whitespace (critical for YAML)
    vim.opt_local.list = true
    vim.opt_local.listchars = { tab = '→ ', trail = '·', nbsp = '␣' }

    -- Folding by indentation for YAML
    vim.opt_local.foldmethod = 'indent'
    vim.opt_local.foldlevelstart = 99  -- Start with all folds open
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
      require('tokyonight').setup({
        style = 'night',
        on_highlights = function(hl, c)
          -- Enhanced YAML highlighting
          hl['@field.yaml'] = { fg = c.blue, bold = true }            -- Keys (brighter blue, bold)
          hl['@string.yaml'] = { fg = c.green }                       -- Values (green)
          hl['@punctuation.delimiter.yaml'] = { fg = c.fg_dark }      -- Colons (subtle)
          hl['@punctuation.special.yaml'] = { fg = c.orange }         -- Special chars (-, |, >)
          hl['@number.yaml'] = { fg = c.orange }                      -- Numbers
          hl['@boolean.yaml'] = { fg = c.magenta }                    -- true/false
          hl['@constant.yaml'] = { fg = c.cyan }                      -- Constants
          hl['@comment.yaml'] = { fg = c.comment, italic = true }     -- Comments
        end,
      })
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
        highlight = {
          enable = true,
          additional_vim_regex_highlighting = false,
        },
        indent = { enable = true },
      })
    end,
  },

  -- Indent guides (essential for YAML)
  {
    'lukas-reineke/indent-blankline.nvim',
    main = 'ibl',
    config = function()
      require('ibl').setup({
        indent = {
          char = '│',
          tab_char = '│',
        },
        scope = {
          enabled = true,
          show_start = true,
          show_end = false,
        },
        exclude = {
          filetypes = { 'help', 'alpha', 'dashboard', 'neo-tree', 'Trouble', 'lazy' },
        },
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

-- Claude AI integration (uses ~/.dotfiles/local/bin/ai)
local claude = {}

-- Get visual selection
claude.get_selection = function()
  local start_pos = vim.fn.getpos("'<")
  local end_pos = vim.fn.getpos("'>")
  local lines = vim.fn.getline(start_pos[2], end_pos[2])
  if #lines == 0 then return '' end
  -- Handle partial line selection
  lines[#lines] = string.sub(lines[#lines], 1, end_pos[3])
  lines[1] = string.sub(lines[1], start_pos[3])
  return table.concat(lines, '\n')
end

-- Run ai command and return result
claude.ask = function(prompt, text)
  local cmd = string.format('echo %s | ai --raw %s', vim.fn.shellescape(text), vim.fn.shellescape(prompt))
  local result = vim.fn.system(cmd)
  return vim.trim(result)
end

-- Replace selection with AI response
claude.replace = function(prompt)
  local text = claude.get_selection()
  if text == '' then
    vim.notify('No selection', vim.log.levels.WARN)
    return
  end
  local result = claude.ask(prompt, text)
  -- Replace the visual selection
  vim.cmd('normal! gv"_d')
  vim.api.nvim_put(vim.split(result, '\n'), 'c', false, true)
end

-- Show AI response in split (keeps original)
claude.show = function(prompt)
  local text = claude.get_selection()
  if text == '' then
    vim.notify('No selection', vim.log.levels.WARN)
    return
  end
  local result = claude.ask(prompt, text)
  -- Open result in horizontal split
  vim.cmd('new')
  vim.api.nvim_buf_set_lines(0, 0, -1, false, vim.split(result, '\n'))
  vim.bo.buftype = 'nofile'
  vim.bo.filetype = 'markdown'
end

-- Interactive prompt
claude.prompt = function(action)
  vim.ui.input({ prompt = 'Claude: ' }, function(input)
    if input and input ~= '' then
      if action == 'replace' then
        claude.replace(input)
      else
        claude.show(input)
      end
    end
  end)
end

-- Keymaps (visual mode)
keymap('v', '<leader>aa', function() claude.prompt('show') end, { desc = 'Ask Claude' })
keymap('v', '<leader>ar', function() claude.prompt('replace') end, { desc = 'Ask Claude (replace)' })
keymap('v', '<leader>ae', function() claude.show('Explain this code concisely') end, { desc = 'Explain' })
keymap('v', '<leader>af', function() claude.replace('Fix this code. Return only the fixed code, no explanation.') end, { desc = 'Fix' })
keymap('v', '<leader>as', function() claude.replace('Simplify this code. Return only the code, no explanation.') end, { desc = 'Simplify' })
keymap('v', '<leader>ad', function() claude.show('Add documentation/comments to this code') end, { desc = 'Document' })
