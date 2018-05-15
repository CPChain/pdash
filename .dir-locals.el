((python-mode . ((eval . (set (make-local-variable 'my-project-path)
                              (file-name-directory
                               (let ((d (dir-locals-find-file ".")))
                                 (if (stringp d) d (car d))))))
                 (eval . (setq flycheck-pylintrc "pylintrc"))
                 (eval . (add-to-list 'python-shell-extra-pythonpaths my-project-path))
                 (eval . (hs-minor-mode))
                 (eval . (flycheck-mode)))))
