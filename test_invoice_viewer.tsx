import React from 'react';

const InvoiceViewer = ({invoice}: {invoice: {amount: number, currency: string}}) => (
  <div>Amount: {invoice.amount} {invoice.currency}</div>
);

export default InvoiceViewer;
