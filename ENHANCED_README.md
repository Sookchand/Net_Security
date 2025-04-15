# Enhanced Network Security API

This is an enhanced version of the Network Security API with advanced visualization and interactive features.

## Features

The enhanced version includes:

1. **Interactive Visualizations**
   - Pie chart showing the distribution of attack types
   - Bar chart displaying attack counts
   - Color-coded results for easy identification

2. **Filtering and Sorting**
   - Filter results by attack type
   - See counts of filtered records

3. **Export Options**
   - Export results as CSV
   - Print-friendly view

4. **Improved UI**
   - Modern, responsive design
   - Dashboard layout
   - Summary statistics

## Deployment

### Option 1: Using the Python Deployment Script

```bash
python deploy.py --key my-key-pair.pem --host ec2-3-87-239-199.compute-1.amazonaws.com --enhanced
```
"""
(venv)
python deploy.py --key my-key-pair.pem --host ec2-3-87-239-199.compute-1.amazonaws.com --enhanced
"""

The `--enhanced` flag tells the script to deploy the enhanced version.

### Option 2: Manual Deployment

1. Upload the files to your EC2 instance:
   ```bash
   scp -i my-key-pair.pem enhanced_very_simple_app.py ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
   scp -i my-key-pair.pem Dockerfile.enhanced ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
   scp -i my-key-pair.pem requirements.very_simple.txt ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
   scp -i my-key-pair.pem deploy_enhanced.sh ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
   scp -i my-key-pair.pem sample_network_data.csv ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com:~/
   ```

2. SSH into your EC2 instance:
   ```bash
   ssh -i my-key-pair.pem ec2-user@ec2-3-87-239-199.compute-1.amazonaws.com
   ```

3. Make the deployment script executable and run it:
   ```bash
   chmod +x deploy_enhanced.sh
   ./deploy_enhanced.sh
   ```

## Using the Application

1. Access the application at `http://your-ec2-instance:8000`
2. Use the "Train Model" button to simulate training
3. Upload a CSV file using the "Make Predictions" form
4. Explore the interactive results page:
   - View the summary statistics
   - Interact with the pie and bar charts
   - Filter results by attack type
   - Export results as CSV or print them

## Screenshots

The enhanced version includes:

1. **Dashboard View**
   - Summary statistics
   - Pie chart and bar chart visualizations
   - Detailed results table

2. **Interactive Features**
   - Filtering by attack type
   - Export options
   - Responsive design

## Technical Details

The enhanced version uses:

- **Chart.js**: For interactive visualizations
- **FastAPI**: For the backend API
- **Jinja2 Templates**: For server-side rendering
- **CSS Grid**: For responsive layout
- **Docker**: For containerization

## Troubleshooting

If you encounter any issues:

1. Check the container logs:
   ```bash
   docker logs netwroksecuritytrial
   ```

2. Verify that all files were uploaded correctly:
   ```bash
   ls -la ~/
   ```

3. Make sure the container is running:
   ```bash
   docker ps | grep netwroksecuritytrial
   ```

4. Check for any errors in the deployment script:
   ```bash
   cat deploy_enhanced.sh
   ```
