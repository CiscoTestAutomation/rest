#### Contribute to the documentation

Documentation is made better when user can provide feedback and provide enhancement. pyATS strongly encourages community involvement in improving the documentation.

To contribute, you need to fork the repository, do your modifications and create a new pull request. 

> :warning: **Make sure you have the full pyats package installed via ```pip install pyats[full]```.**

To build the docs locally on your machine. Please follow the instructions below 

  - On the top right corner, click ```Fork```. (see https://help.github.com/en/articles/fork-a-repo)

<img width="421" alt="Screen Shot 2020-12-21 at 2 37 19 PM" src="https://user-images.githubusercontent.com/30438439/102815289-1e75e700-439a-11eb-92bc-e424ddce9758.png">

  - In your terminal, clone the repo using the command shown below: 
    ```shell
    git clone https://github.com/<your_github_username>/rest.git
    ```

  - ```cd rest/docs```
  
  - Use ```make install_build_deps```  to install all of the build dependencies
  
  - Run ```make docs``` to generate documentation in HTML

  - Wait until you see ```Done``` in your terminal
  
  - The documentation is now built and stored under the directory 
  ```rest/__build__```

  - Run ```make serve``` to view the documentation on your browser or navigate to the repository.
    
  - Please create a PR after you have made your changes (see [commit your changes](https://pubhub.devnetcloud.com/media/pyats-development-guide/docs/contribute/contribute.html#commit-your-changes) & [open a PR](https://pubhub.devnetcloud.com/media/pyats-development-guide/docs/contribute/contribute.html#open-a-pull-request))

Here are a few examples that could be great pull request:

- Fix Typos
- Better wording, easier explanation
- More details, examples
- Anything else to enhance the documentation

#### How to contribute to the pyATS community

- For detail on contributing to pyATS, please follow the [contribution guidelines](https://pubhub.devnetcloud.com/media/pyats-development-guide/docs/contribute/contribute.html#)
