#./plot -s ../data/output_data_rms_002/new/ --load config/plotcard_data_vbf.json   --all --label rms_002   --title "PromptReco 74x","VBF preselection","100 < m_{#gamma#gamma} < 180 GeV","Jet RMS(|#eta|>2.5) < 0.02"
./plot -s ../data/output_data_rms_003/new/new --load config/plotcard_data_vbf.json   -v combined_BDT --label rms   --title "PromptReco 74x","VBF preselection","100 < m_{#gamma#gamma} < 180 GeV","Jet RMS(|#eta|>2.5) < 0.03"
./plot -s ../data/output_data_rms_003/new/new --load config/plotcard_data_vbf.json   -v dijet_BDT --label rms   --title "PromptReco 74x","VBF preselection","100 < m_{#gamma#gamma} < 180 GeV","Jet RMS(|#eta|>2.5) < 0.03"
#./plot -s ../data/output_data_rms_004/new/ --load config/plotcard_data_vbf.json   --all --label rms_004   --title "PromptReco 74x","VBF preselection","100 < m_{#gamma#gamma} < 180 GeV","Jet RMS(|#eta|>2.5) < 0.04"

#./plot -s ../data/output_data_rms_002/new/ --load config/plotcard_data_vbf_dipho.json   --all --label rms_002   --title "PromptReco 74x","Diphoton preselection","100 < m_{#gamma#gamma} < 180 GeV","Jet RMS(|#eta|>2.5) < 0.02"
./plot -s ../data/output_data_rms_003/new/new --load config/plotcard_data_vbf_dipho.json -v combined_BDT --label rms   --title "PromptReco 74x","Diphoton preselection","100 < m_{#gamma#gamma} < 180 GeV","Jet RMS(|#eta|>2.5) < 0.03"
./plot -s ../data/output_data_rms_003/new/new --load config/plotcard_data_vbf_dipho.json -v dijet_BDT --label rms   --title "PromptReco 74x","Diphoton preselection","100 < m_{#gamma#gamma} < 180 GeV","Jet RMS(|#eta|>2.5) < 0.03"
#./plot -s ../data/output_data_rms_004/new/ --load config/plotcard_data_vbf_dipho.json   --all --label rms_004   --title "PromptReco 74x","Diphoton preselection","100 < m_{#gamma#gamma} < 180 GeV","Jet RMS(|#eta|>2.5) < 0.04"

#./plot -s ../data/output_data_rms_002/new/ --load config/plotcard_signal_vbf_dipho.json --all --label rms_002 --title "PromptReco 74x","Diphoton preselection","100 < m_{#gamma#gamma} < 180 GeV","Jet RMS(|#eta|>2.5) < 0.02"
#./plot -s ../data/output_data_rms_003/new/new --load config/plotcard_signal_vbf_dipho.json -v dijet_BDT --label dipho --title "PromptReco 74x","Diphoton preselection","100 < m_{#gamma#gamma} < 180 GeV","Jet RMS(|#eta|>2.5) < 0.03"
#./plot -s ../data/output_data_rms_003/new/new --load config/plotcard_signal_vbf.json -v dijet_BDT vbf --title "PromptReco 74x","VBF preselection","100 < m_{#gamma#gamma} < 180 GeV","Jet RMS(|#eta|>2.5) < 0.03"

#./plot -s ../data/output_data_rms_003/new/new --load config/plotcard_signal_vbf_dipho.json -v combined_BDT --label dipho --title "PromptReco 74x","Diphoton preselection","100 < m_{#gamma#gamma} < 180 GeV","Jet RMS(|#eta|>2.5) < 0.03"
#./plot -s ../data/output_data_rms_003/new/new --load config/plotcard_signal_vbf.json -v combined_BDT vbf --title "PromptReco 74x","VBF preselection","100 < m_{#gamma#gamma} < 180 GeV","Jet RMS(|#eta|>2.5) < 0.03"


#./plot -s ../data/output_data_rms_004/new/ --load config/plotcard_signal_vbf_dipho.json --all --label rms_004 --title "PromptReco 74x","Diphoton preselection","100 < m_{#gamma#gamma} < 180 GeV","Jet RMS(|#eta|>2.5) < 0.04"

#./plot -s ../data/output_data_rms_002/new/ --load config/plotcard_signal_vbf.json --all --label rms_002   --title "PromptReco 74x","VBF preselection","100 < m_{#gamma#gamma} < 180 GeV","Jet RMS(|#eta|>2.5) < 0.02"

#./plot -s ../data/output_data_rms_004/new/ --load config/plotcard_signal_vbf.json --all --label rms_004   --title "PromptReco 74x","VBF preselection","100 < m_{#gamma#gamma} < 180 GeV","Jet RMS(|#eta|>2.5) < 0.04"


#./plot -s ../data/merged_zee_rms_1_2_0/        --load config/plotcard_zee_vbf.json   --all --title "PromptReco 74x","VBF preselection","70 < m_{#gamma#gamma} < 110 GeV"
#./plot -s ../data/merged_zee_rms_1_2_0/        --load config/plotcard_zee_dipho.json --all --title "PromptReco 74x","Diphoton preselection","70 < m_{#gamma#gamma} < 110 GeV"
