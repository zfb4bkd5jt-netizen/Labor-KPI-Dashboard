import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
d=[r for r in json.load(open('/tmp/bscq.json')) if r['z']>='2025']
for key,name,soll,fn in [('tt','Termintreue',65,'tt.png'),('be','Budgeteinhaltung',80,'be.png'),('ql','Qualitätslevel',80,'ql.png')]:
    fig,ax=plt.subplots(figsize=(6.0,4.2),dpi=160)
    lab=[r['z'][5:]+"\n"+r['z'][:4]+(" (lfd.)" if r['lauf'] else "") for r in d]
    v=[r[key] for r in d]
    xs=range(len(d))
    farbe=['#2a6fdb' if (x is not None and x>=soll) else '#d9534f' for x in v]
    ax.bar([i for i,x in zip(xs,v) if x is not None],[x for x in v if x is not None],color=[f for f,x in zip(farbe,v) if x is not None],width=0.65)
    for i,x in zip(xs,v):
        ax.text(i,(x or 0)+1.5,'kein Wert' if x is None else f"{x:.1f}".replace('.',','),ha='center',va='bottom',fontsize=8,color='#333' if x is not None else '#999')
    ax.axhline(soll,ls='--',color='#444',lw=1); ax.text(-0.45,soll+1,f"SOLL ≥ {soll} %",ha="left",va='bottom',fontsize=8,color='#444')
    ax.set_xticks(list(xs)); ax.set_xticklabels(lab,fontsize=7)
    ax.set_ylim(0,max(110,max(x for x in v if x)+10)); ax.set_ylabel('%',fontsize=8); ax.tick_params(axis='y',labelsize=7)
    ax.set_title(f"{name} je Quartal (Datenstand 04.11.2026)",fontsize=9)
    for s in ('top','right'): ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(fn); plt.close(fig)
print('ok')
