# Jenkins Pipeline Configuration Guide

## Problem
Your Jenkins job is currently configured as a **Freestyle project**, which only performs a git checkout. It doesn't execute the `Jenkinsfile` pipeline stages.

## Solution
You need to convert your job to a **Pipeline project** or create a new Pipeline job.

## Steps to Configure Jenkins Pipeline

### Option 1: Create a New Pipeline Job (Recommended)

1. **Go to Jenkins Dashboard**
   - Click "New Item"

2. **Create Pipeline Job**
   - Enter a name (e.g., "DataBase2-Pipeline")
   - Select "Pipeline"
   - Click "OK"

3. **Configure Pipeline**
   - Scroll down to the "Pipeline" section
   - For "Definition", select: **Pipeline script from SCM**
   
4. **Configure SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/AHML47/5edmet-mas3oud`
   - Branch Specifier: `*/il-file-wil-user-wil-code-yemchiw` (or your branch name)
   
5. **Script Path**
   - **IMPORTANT:** Your repository has `DataBase2` as a subdirectory
   - Script Path: **`DataBase2/Jenkinsfile`**
   - ⚠️ If this doesn't work, check your repository structure on GitHub
   - The path must match where the Jenkinsfile is located in your repository

6. **Save and Build**
   - Click "Save"
   - Click "Build Now"

### Option 2: Modify Existing Job

1. **Go to your existing job** ("projet integration")
2. Click "Configure"
3. **Change project type:**
   - You may need to delete and recreate as a Pipeline job
   - Jenkins doesn't allow changing job types directly

## Expected Output

Once configured correctly, you should see:

```
Started by user admin
Running in Durability level: MAX_SURVIVABILITY
[Pipeline] Start of Pipeline
[Pipeline] node
[Pipeline] {
[Pipeline] stage
[Pipeline] { (Checkout)
...
[Pipeline] stage
[Pipeline] { (Setup Environment)
...
[Pipeline] stage
[Pipeline] { (Run Tests)
...
🚀 Starting API Tests with SQLite...
test_01_health ... ok
test_02_unauthorized ... ok
test_03_create_user ... ok
test_04_get_users ... ok
test_05_create_activity ... ok
test_06_get_activities ... ok
...
OK
[Pipeline] }
[Pipeline] // stage
[Pipeline] End of Pipeline
Finished: SUCCESS
```

## Troubleshooting

### If tests fail in Jenkins but pass locally:
- Ensure Python and pip are installed in the Jenkins agent
- Check that `requirements.txt` is being installed correctly
- Verify the workspace path doesn't have spaces (Jenkins issue)

### If Jenkinsfile is not found:
- Verify the "Script Path" matches your repository structure
- In your case, it should be: `DataBase2/Jenkinsfile`
- Make sure the Jenkinsfile is committed and pushed to the branch

## Verification

After configuration, trigger a build and you should see:
- ✅ 4 model tests passing
- ✅ 6 API tests passing
- ✅ Total: 10 tests passing
