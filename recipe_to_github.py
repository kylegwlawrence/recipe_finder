import git

repo = git.Repo('/Users/kylelawrence/Documents/recipe_finder') 
  
# Do some changes and commit 
file1 = 'test-sample.jpg'
file2 = 'input.txt'
repo.index.add([file1,file2]) 
print('Files Added Successfully') 
repo.index.commit('Initial commit on new branch') 
print('Commited successfully')