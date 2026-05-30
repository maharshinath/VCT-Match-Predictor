import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import {BrowserRouter as Router, Routes, Route} from 'react-router-dom'
import './css/App.css'
import NavBar from './components/Navbar'
import About from './pages/About'
import MakePrediction from './pages/MakePrediction'
import PredictionPage from './pages/PredictionPage'


function App() {


  return (
    <div>
      <NavBar />
      <main className="main-content">
          <Routes>
            <Route path='/' element={<MakePrediction />} />
            <Route path='/about' element={<About />} />
            <Route path='/predict/:team1/:team2' element={<PredictionPage />} />
          </Routes>
      </main>
    </div>
  )
}

export default App
