" Vim syntax file for SheerPower 4GL
" Language: SheerPower 4GL
" Maintainer: Sheerpower project
" Filenames: *.spsrc, *.spinc
" Generated from: src/sheerpower/lang/lexer.py  (single source of truth)
"
" Installation:
"   Symlink or copy etc/nvim/ into your Neovim config directory:
"     ln -s $(pwd)/etc/nvim/syntax  ~/.config/nvim/syntax
"     ln -s $(pwd)/etc/nvim/ftdetect ~/.config/nvim/ftdetect
"     ln -s $(pwd)/etc/nvim/ftplugin ~/.config/nvim/ftplugin
"   Or add the repo root to runtimepath in your init.lua / init.vim:
"     vim.opt.runtimepath:prepend('/path/to/sheerpower/etc/nvim')

if exists("b:current_syntax")
  finish
endif

" Case-insensitive — SheerPower keywords are case-insensitive
syntax case ignore

" ── Control Flow ─────────────────────────────────────────────────────────────
syntax keyword spStatement
      \ print input prompt let stop delay pass call
      \ open close all file line
      \ add delete reset collect copy
      \ sort extract
      \ clear

syntax keyword spConditional    if then else elseif end
syntax keyword spRepeat         for to step next while until do loop exit iterate
syntax keyword spException      when exception use continue retry handler in

" ── Declarations ─────────────────────────────────────────────────────────────
syntax keyword spStructure      routine local private module cluster table
syntax keyword spDeclaration    dim const declare enum program

" ── Built-in Operators (word form) ───────────────────────────────────────────
syntax keyword spOperator       and or not mod is by ascending descending
syntax keyword spOperator       from include exclude unique nowait using select case

" ── Type Keywords ────────────────────────────────────────────────────────────
syntax keyword spType           real string integer boolean dynamic

" ── Built-in Functions (dollar-suffix) ───────────────────────────────────────
" format$ is a keyword in the lexer; the rest are runtime library names
syntax keyword spBuiltin        format$
syntax keyword spBuiltin
      \ len left$ right$ mid$ trim$ ltrim$ rtrim$ ucase$ lcase$
      \ pos replace$ piece$ pieces element$ edit$ str$ val chr$ ord
      \ space$ repeat$ lpad$ rpad$ cpad$ match getword$
      \ base64encode$ base64decode$ regex_match$ sprintf$
syntax keyword spBuiltin
      \ abs int mod rnd round sqr log log10 exp sin cos tan atn max min
syntax keyword spBuiltin
      \ size date$ time$ days

" ── Preprocessor Directives ──────────────────────────────────────────────────
syntax match spPreproc          /^\s*%\(define\|include\|if\|else\|end\s*%if\|todo\|compile\)\>/
syntax match spPreproc          /^\s*%todo\>.*$/

" ── Comments ─────────────────────────────────────────────────────────────────
syntax match spComment          /!.*$/
syntax match spComment          /\/\/.*$/

" ── Strings ──────────────────────────────────────────────────────────────────
syntax region spString          start=/'/ skip=/''/ end=/'/
syntax region spString          start=/"/ skip=/""/ end=/"/

" ── Numbers ──────────────────────────────────────────────────────────────────
syntax match spNumber           /\<\d\+\(\.\d\+\)\?\>/
syntax match spNumber           /\<\d\+_\d\+\(_\d\+\)*\>/

" ── Type Suffixes on identifiers ─────────────────────────────────────────────
syntax match spTypeSuffix       /\w\+\([$%?]\)/

" ── Linking to standard Vim highlight groups ─────────────────────────────────
highlight default link spStatement      Statement
highlight default link spConditional    Conditional
highlight default link spRepeat         Repeat
highlight default link spException      Exception
highlight default link spStructure      Structure
highlight default link spDeclaration    Type
highlight default link spOperator       Operator
highlight default link spType           Type
highlight default link spBuiltin        Function
highlight default link spPreproc        PreProc
highlight default link spComment        Comment
highlight default link spString         String
highlight default link spNumber         Number
highlight default link spTypeSuffix     Special

let b:current_syntax = "sheerpower"
