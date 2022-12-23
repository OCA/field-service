pipeline {
  agent any
  stages {
    stage('pre-commit') {
      steps {
        sh 'pip install pre-commit'
        sh 'pre-commit run --all-files --show-diff-on-failure --color=always'
        sh '''
          newfiles="$(git ls-files --others --exclude-from=.gitignore)"
          if [ "$newfiles" != "" ] ; then
              echo "Please check-in the following files:"
              echo "$newfiles"
              exit 1
          fi
        '''
      }
    }
  }
}
