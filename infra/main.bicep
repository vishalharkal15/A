targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Id of the user or app to assign application roles')
param principalId string = ''

// Optional parameters
@description('Name of the resource group')
param resourceGroupName string = ''

@description('Name of the App Service Plan')
param appServicePlanName string = ''

@description('Name of the Web App')
param webAppName string = ''

@description('Name of the PostgreSQL server')
param databaseServerName string = ''

@description('Name of the PostgreSQL database')
param databaseName string = 'attendancedb'

@description('Administrator username for PostgreSQL')
@secure()
param databaseAdminUsername string = 'attendanceadmin'

@description('Administrator password for PostgreSQL')
@secure()
param databaseAdminPassword string

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

// Organize resources in a resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

// Application Insights
module appInsights './appinsights.bicep' = {
  name: 'appinsights'
  scope: rg
  params: {
    name: '${abbrs.insightsComponents}${resourceToken}'
    location: location
    tags: tags
  }
}

// Main resources
module resources './resources.bicep' = {
  name: 'resources'
  scope: rg
  params: {
    location: location
    tags: tags
    principalId: principalId
    appServicePlanName: !empty(appServicePlanName) ? appServicePlanName : '${abbrs.webServerFarms}${resourceToken}'
    webAppName: !empty(webAppName) ? webAppName : '${abbrs.webSitesAppService}${resourceToken}'
    databaseServerName: !empty(databaseServerName) ? databaseServerName : '${abbrs.dBforPostgreSQLServers}${resourceToken}'
    databaseName: databaseName
    databaseAdminUsername: databaseAdminUsername
    databaseAdminPassword: databaseAdminPassword
    appInsightsConnectionString: appInsights.outputs.connectionString
  }
}

// Output values
output AZURE_LOCATION string = location
output AZURE_RESOURCE_GROUP string = rg.name
output WEB_APP_NAME string = resources.outputs.webAppName
output DATABASE_URL string = resources.outputs.databaseConnectionString
output APPLICATIONINSIGHTS_CONNECTION_STRING string = appInsights.outputs.connectionString
