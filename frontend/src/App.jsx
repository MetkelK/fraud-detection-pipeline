import StatsCards from './components/StatsCards'
import FraudByTypeChart from './components/FraudByTypeChart'
import FraudOverTimeChart from './components/FraudOverTimeChart'
import ModelInfo from './components/ModelInfo'
import TransactionValidator from './components/TransactionValidator'

function App() {
  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px' }}>
      <h1>Fraud Detection Dashboard</h1>
      <StatsCards />
      <FraudByTypeChart />
      <FraudOverTimeChart />
      <ModelInfo />
      <TransactionValidator />
    </div>
  )
}

export default App