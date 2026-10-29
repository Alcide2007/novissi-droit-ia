import React from 'react';
import { Outlet } from 'react-router-dom';

const Layout: React.FC = () => {
  return (
    <>
      <header className="mobile-header">
        {/* Your header content */}
      </header>
      
      {/* The main container inherits flex properties from styles.css */}
      <main>
        <Outlet />
      </main>
      
      {/* Bottom navigation bar */}
      <nav className="mobile-bottom-nav">
         {/* Nav items */}
      </nav>
    </>
  );
};

export default Layout;
