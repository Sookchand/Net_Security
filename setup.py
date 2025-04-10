'''
The setup.py file is an essential part of packaging and 
distributing Python projects. It is used by setuptools 
(or distutils in older Python versions) to define the configuration 
of your project, such as its metadata, dependencies, and more
'''

from setuptools import find_packages,setup
from typing import List # List is imported from typing module

# This is a variable that contains the name of the file that contains the list of requirements
REQUIREMENT_FILE_NAME='requirements.txt' # This is the name of the file that contains the list of requirements

def get_requirements()->List[str]:
    """
    This function will return list of requirements
    
    """
    requirement_lst:List[str]=[]
    try:
        with open('requirements.txt','r') as file:
            #Read lines from the file
            lines=file.readlines()
            ## Process each line
            for line in lines:
                requirement=line.strip()
                ## ignore empty lines and -e .
                if requirement and requirement!= '-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("requirements.txt file not found")

    return requirement_lst

# print(get_requirements())

# The setup() function is called to define the package metadata and configuration
# The parameters passed to the setup() function include:    
# name: The name of the package.
# version: The version of the package.
setup(
    name="NetworkSecurity",
    version="0.0.1",    
    author="Sookchand Harripersad",
    author_email="sookchand@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements(),
)