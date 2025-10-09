
import type { RouteObject } from "react-router-dom";
import NotFound from "../pages/NotFound";
import Home from "../pages/home/page";
import Login from "../pages/login/page";
import Dashboard from "../pages/dashboard/page";
import Profile from "../pages/profile/page";
import Settings from "../pages/settings/page";
import SurveillanceDashboard from "../pages/surveillance/SurveillanceDashboard";
import SurveillanceConfig from "../pages/surveillance/SurveillanceConfig";

const routes: RouteObject[] = [
  {
    path: "/",
    element: <Home />,
  },
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/dashboard",
    element: <Dashboard />,
  },
  {
    path: "/surveillance",
    element: <SurveillanceDashboard />,
  },
  {
    path: "/surveillance/config",
    element: <SurveillanceConfig />,
  },
  {
    path: "/profile",
    element: <Profile />,
  },
  {
    path: "/settings",
    element: <Settings />,
  },
  {
    path: "*",
    element: <NotFound />,
  },
];

export default routes;
