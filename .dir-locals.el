((nil . ((eval . (set (make-local-variable 'my-project-path)
                      (file-name-directory
                       (let ((d (dir-locals-find-file ".")))
                         (if (stringp d) d (car d))))))
         (eval . (add-to-list 'python-shell-extra-pythonpaths my-project-path)))))
