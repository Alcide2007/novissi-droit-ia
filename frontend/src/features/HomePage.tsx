import React from 'react';
import { useTranslation } from 'react-i18next';
// Import your components (ChatInput, etc.)
// import ChatInput from '../components/ChatInput';

const HomePage: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>{t('greeting')}</h1>
        <p>{t('how_can_i_help')}</p>
      </div>

      {/* Note: The 4 quick suggestion cards have been removed as requested */}
      
      {/* 
        This is where your chat messages would go.
        Ensure this container can scroll independently if needed, 
        or let the whole page scroll. 
      */}
      <div className="chat-messages" style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
        {/* Messages */}
      </div>

      <div className="chat-input-wrapper">
         {/* <ChatInput /> */}
         <input type="text" placeholder={t('type_message')} style={{width: '100%', padding: '12px'}} />
      </div>
    </div>
  );
};

export default HomePage;
