@description('The name of the Application Insights resource')
param name string

@description('Location for the Application Insights resource')
param location string = resourceGroup().location

@description('Tags to apply to the resource')
param tags object = {}

@description('The type of application being monitored')
param applicationType string = 'web'

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: name
  location: location
  tags: tags
  kind: applicationType
  properties: {
    Application_Type: applicationType
    Flow_Type: 'Bluefield'
    Request_Source: 'rest'
    RetentionInDays: 30
    IngestionMode: 'ApplicationInsights'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

@description('The instrumentation key of the Application Insights resource')
output instrumentationKey string = appInsights.properties.InstrumentationKey

@description('The connection string of the Application Insights resource')
output connectionString string = appInsights.properties.ConnectionString

@description('The resource ID of the Application Insights resource')
output id string = appInsights.id
