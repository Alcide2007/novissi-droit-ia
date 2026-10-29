import React from 'react';
import { useTranslation } from 'react-i18next';

const TerraCheckPage: React.FC = () => {
  const { t } = useTranslation();

  return (
    // Crucial: No inline styles restricting height here (like height: '100vh', overflow: 'hidden')
    <div className="terracheck-container">
      <h1>{t('terracheck_title')}</h1>
      <p>{t('terracheck_description')}</p>
      
      <div className="form-grid">
         {/* Form fields with adapted styling from styles.css */}
         <div className="form-group">
           <label>{t('parcel_number')}</label>
           <input type="text" />
         </div>
         <div className="form-group">
           <label>{t('location')}</label>
           <input type="text" />
         </div>
         <button className="submit-btn">{t('verify')}</button>
      </div>
    </div>
  );
};

export default TerraCheckPage;
