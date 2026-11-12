import { NavLink } from "react-router-dom";


export default function Navbar() {
  const linkClass = ({ isActive }) => (isActive ? "nav-link active" : "nav-link");

  return (
    <header className="navbar">
      <NavLink className="brand" to="/" aria-label="CampusFind home">
        <span className="brand-mark" aria-hidden="true">CF</span>
        <span>CampusFind</span>
      </NavLink>
      <nav aria-label="Main navigation">
        <NavLink end className={linkClass} to="/">Find an item</NavLink>
        <NavLink className={linkClass} to="/report">Report found item</NavLink>
        <NavLink className={linkClass} to="/status">Check status</NavLink>
      </nav>
    </header>
  );
}
