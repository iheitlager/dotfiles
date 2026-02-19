" SheerPower 4GL filetype detection
" Derived from: src/sheerpower/lang/lexer.py
" Install: symlink or copy etc/nvim/ contents to ~/.config/nvim/
"
" Detects .spsrc (source) and .spinc (include) files as filetype=sheerpower

augroup SheerPowerFtDetect
  autocmd!
  autocmd BufNewFile,BufRead *.spsrc setfiletype sheerpower
  autocmd BufNewFile,BufRead *.spinc setfiletype sheerpower
augroup END
