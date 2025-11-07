# Infrastructure as Code (IaC)

This directory contains Bicep templates for deploying the Automated Attendance application to Azure.

## Files

- **main.bicep**: Main orchestration template that defines the subscription-level deployment
- **resources.bicep**: Defines the core Azure resources (App Service, PostgreSQL, etc.)
- **appinsights.bicep**: Application Insights configuration for monitoring
- **main.parameters.json**: Parameter file for the deployment

## Resources Deployed

1. **Resource Group**: Container for all resources
2. **App Service Plan**: Linux-based Basic (B1) tier
3. **Web App**: Python 3.11 application hosting
4. **PostgreSQL Flexible Server**: Database for attendance data
5. **Application Insights**: Monitoring and telemetry

## Prerequisites

- Azure CLI installed
- Azure Developer CLI (azd) installed (optional)
- Valid Azure subscription

## Deployment

### Using Azure Developer CLI (azd)

```bash
# Login to Azure
azd auth login

# Initialize the project (first time only)
azd init

# Provision and deploy
azd up
```

### Using Azure CLI

```bash
# Login to Azure
az login

# Create deployment
az deployment sub create \
  --location eastus \
  --template-file main.bicep \
  --parameters main.parameters.json \
  --parameters environmentName=attendance-prod \
              location=eastus \
              principalId=$(az ad signed-in-user show --query id -o tsv) \
              databaseAdminPassword='YourSecurePassword123!'
```

## Environment Variables

Set these environment variables before deployment:

- `AZURE_ENV_NAME`: Name of your environment (e.g., "attendance-prod")
- `AZURE_LOCATION`: Azure region (e.g., "eastus")
- `AZURE_PRINCIPAL_ID`: Your Azure AD user/app ID
- `DATABASE_ADMIN_PASSWORD`: Secure password for PostgreSQL

## Post-Deployment

After deployment, configure these in the Azure Portal or via CLI:

1. Set the `SECRET_KEY` environment variable in App Service
2. Configure CORS origins in App Service settings
3. Review and adjust PostgreSQL firewall rules as needed
4. Set up custom domain (optional)

## Cost Estimation

Approximate monthly costs (as of 2025):
- App Service Plan (B1): ~$13/month
- PostgreSQL Flexible Server: ~$15/month
- Application Insights: Pay-as-you-go (typically <$5/month for small apps)

**Total**: ~$30-35/month

## Cleanup

To delete all resources:

```bash
# Using azd
azd down

# Using Azure CLI
az group delete --name <resource-group-name>
```
