"""Regression checks against retained public SOURCE captures. No ADB or network."""
import json
from unittest.mock import patch
from h02_device import ROOT
import h02_package as p
from b2r2_acceptance import check
import b2r2_export
def main():
    root=ROOT/'runs/wo3b2';oracle=root/'oracle-deposit.json';results=[]
    for label,auditname in [('dao-settled','dao-compensation-audit-first.json'),('preH2-restart','dao-compensation-audit-restart.json')]:
        obs=root/'source'/label;audit=root/'source'/auditname
        p.require(check(obs,oracle,22647433,position_only=True)['result']=='POSITION_ONLY_PASS','position-regression')
        for name,kwargs,code in [('missing-audit',{},'dao-compensation-not-validated'),('observed-bad-compensation',{'dao_audit':audit},'dao-compensation-noncanonical-or-unresolved')]:
            try:check(obs,oracle,22647433,**kwargs)
            except p.Refused as e:p.require(str(e)==code,'wrong-rejection');results.append({'observation':label,'case':name,'rejected':True,'gate':code})
            else:raise AssertionError('invalid full acceptance')
    obs=root/'source/preH2-restart';audit=root/'source/dao-compensation-audit-restart.json'
    with patch.object(b2r2_export,'rpc',side_effect=AssertionError('RPC reached before source gate')),patch.object(b2r2_export.d,'Device',side_effect=AssertionError('ADB reached before source gate')):
        try:b2r2_export.main(obs,oracle,audit)
        except p.Refused as e:p.require(str(e)=='dao-compensation-noncanonical-or-unresolved','export-rejection')
        else:raise AssertionError('export accepted bad source')
    p.require(not (root/'package-H2').exists() and not (root/'source/coverage.json').exists(),'export-side-effect')
    results.append({'case':'export-refuses-before-RPC-ADB-or-package-creation','rejected':True})
    output={'result':'PASS','scope':'SOURCE compensation and export precondition regressions; not recovery or package-negative proof','cases':results}
    with (root/'source/gate-regression.json').open('xb') as f:f.write(p.encode(output))
    print(json.dumps(output,indent=2))
if __name__=='__main__':main()
