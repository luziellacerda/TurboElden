"""Adds a marked-sample stop before querying or dispatching a Sony emulator."""
from __future__ import annotations
from pathlib import Path

def patch(original:bytes)->bytes:
    text=original.decode('utf-8')
    old='''            try{
                if("ps3".equals(platform))preparePs3(incoming.getData());'''
    new='''            try{
                if(org.emulationstation.frontend.station.StationLocalSonyDemos.isMarkedDemo(this,incoming.getData(),platform)){
                    runOnUiThread(()->demonstration(platform));return;
                }
                if("ps3".equals(platform))preparePs3(incoming.getData());'''
    if text.count(old)!=1:raise ValueError('Original Sony preparation anchor changed')
    text=text.replace(old,new,1)
    old='    private static boolean arm64()'
    new='''    private void demonstration(String platform){
        if(closed||isFinishing())return;
        new AlertDialog.Builder(this).setTitle("Demonstração "+("ps3".equals(platform)?"PS3":"PS4"))
            .setMessage("Este arquivo é apenas um exemplo visual, identificado como DEMO. Não contém um jogo e não será enviado ao emulador. Para jogar, use seu próprio jogo e configure o emulador oficial.")
            .setPositiveButton("Voltar",(d,w)->finish()).setOnCancelListener(d->finish()).show();
    }
    private static boolean arm64()'''
    if text.count(old)!=1:raise ValueError('Original Sony method anchor changed')
    return text.replace(old,new,1).encode('utf-8')
