import {Link} from "react-router-dom"
import '../css/Navbar.css'

function NavBar() {

    return (
        <nav className="navbar glass">
            <div className="app-name">
                <Link to="/">VCT Match Predictor</Link>
            </div>
            <div className="right">
                <Link to="/" className="navbar-link">Home</Link>
                <Link to="/about" className="navbar-link">About</Link>
            </div>
        </nav>
    )
}

export default NavBar