import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import Login from './pages/Login.tsx'
import Content from './pages/Content.tsx';
import FilePredict from './pages/FilePredict.tsx';

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        index: true, 
        element: <Content />,
      },
      {
        path: "file-predict",
        element: <FilePredict />, 
      },
    ],
  },
  {
    path: "login",
    element: <Login />, 
  },
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router}/>
  </StrictMode>,
)
