import { NavLink, Outlet } from "react-router-dom";

// Пункты бокового меню, которые показываются на всех страницах.
const navItems = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/monitors/new", label: "Add Monitor" },
  { to: "/incidents", label: "Incidents" },
];

export default function AppLayout() {
  // Outlet подставляет текущую страницу внутри общей оболочки.
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true" />
          <div>
            <div className="brand-name">CloudPulse</div>
            <div className="brand-subtitle">Visual monitoring</div>
          </div>
        </div>

        <nav className="nav-list" aria-label="Primary navigation">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                isActive ? "nav-link nav-link-active" : "nav-link"
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <main className="main-panel">
        <Outlet />
      </main>
    </div>
  );
}
