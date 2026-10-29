import React,{act} from 'react';
import {createRoot} from 'react-dom/client';
import App from './App';
global.IS_REACT_ACT_ENVIRONMENT=true;
let container,root;
beforeEach(()=>{container=document.createElement('div');document.body.appendChild(container);root=createRoot(container);});
afterEach(()=>{act(()=>root.unmount());container.remove();jest.restoreAllMocks();});
const info={model:'Baseline',training_rows:5634,test_rows:1409,dataset_rows:7043,roc_auc:.83,average_precision:.62,brier_score:.14,baseline_brier:.19,log_loss:.43,baseline_log_loss:.58,test_churn_rate:.26,calibration:[]};
test('shows profile score with its evidence and no invented offer',async()=>{
 global.fetch=jest.fn().mockResolvedValueOnce({ok:true,json:async()=>info}).mockResolvedValueOnce({ok:true,json:async()=>({score:.2,segment_count:100,segment_churn_rate:.25,inputs:{tenure:12},interpretation:'Review score only.'})});
 await act(async()=>root.render(<App/>));
 await act(async()=>container.querySelector('form').dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})));
 expect(container.textContent).toContain('20.0%');
 expect(container.textContent).toContain('Review score only');
 expect(container.textContent).not.toContain('Quality Score');
 expect(JSON.parse(global.fetch.mock.calls[1][1].body).tenure).toBe(12);
});
test('error message is visible without a successful result',async()=>{
 global.fetch=jest.fn().mockResolvedValueOnce({ok:true,json:async()=>info}).mockResolvedValueOnce({ok:false,json:async()=>({detail:'Invalid'})});
 await act(async()=>root.render(<App/>));
 await act(async()=>container.querySelector('form').dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})));
 expect(container.querySelector('[role="alert"]').textContent).toContain('Review the input values');
 expect(container.textContent).not.toContain('Profile churn score');
});
