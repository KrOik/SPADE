KEYS_EXIST = ['Tissue specificity', 'Basic Residues', 'Mechanism of action', 
              'Sequence uncertainty', 'Absent Amino Acids', 'Gene', 
              'Binding Target', 'Half Life', 'Temperature dependence', 
              'Peptide Name', 'Catalytic activity', 'Caution', 
              'Subunit structure', 'Cytotoxicity', 
              'Chemical modification', 'PTM', 'Hydrophobic Residues', 
              'Biotechnological use', 'Medical use', 'Toxic Dose', 
              'Transgenic plants', 'Literature', 'Structure Description', 
              'Induction', 'Formula', 'Hydrophobicity', 'Positive Residues', 
              'Comments', 'Protein Existence', 'UniProt Entry', 
              'Hemolytic Activity', 'Family', 'Target Organism', 
              'Mass', 'C-terminal Modification', 'Biophysicochemical properties', 
              'N-terminal Modification', 'Developmental stage', 'Function', 
              'Sequence Length', 'Polar Residues', 'Reference', 'Net Charge', 
              'Frequent Amino Acids', 'Miscellaneous', 'Negative Residues', 
              'Acidic Residues', 'Source', 'PI', 'Animal model',
              'Linear/Cyclic', 'Sequence', 'Biological Activity', 'Stereochemistry', 
              'Domain', 'Similar Sequences']
def flit_str(string: str) -> bool:
    string = string.strip().lower()
    if string.startswith("no") or string == "" or string.startswith("unknown"):
        return False
    else:
        return True

def process_BA(biological_activity: list) -> str:
    if not biological_activity or (len(biological_activity) == 1 and biological_activity[0].strip().lower() == "unknown"):
        return None
    else:
        return " ".join(f"{i+1}. {item}" for i, item in enumerate(biological_activity))

def process_UE(uniprot_entry) -> str:
    if isinstance(uniprot_entry, str):
        return None
    elif isinstance(uniprot_entry, list):
        if len(uniprot_entry) > 0:
            if isinstance(uniprot_entry[0], str):
                return " ".join(f"{i+1}. {item}" for i, item in enumerate(uniprot_entry))
            elif isinstance(uniprot_entry[0], dict):
                return " ".join(f"{i+1}. [Uniprot ID]{item['uniprotId']} [Uniprot URL]{item['uniprotUrl']}" for i, item in enumerate(uniprot_entry))
    return None

def process_Literature(Literature) -> str:
    if isinstance(Literature, list):
        if len(Literature) > 0:
            if isinstance(Literature[0], dict):
                content = []
                for l in Literature:
                    temp = []
                    keys = list(l.keys())
                    for key in keys:
                        if l[key].strip() != "":
                            temp.append(f"[{key}]: {l[key]}")
                        else:
                            continue
                    content.append("; ".join(temp))
                return " ".join(f"{i+1}. {item}" for i, item in enumerate(content))
            else:
                return None
        else:
            return None
    elif isinstance(Literature, dict):
        content = []
        keys = list(Literature.keys())
        for key in keys:
            if Literature[key].strip() != "":
                content.append(f"[{key}]: {Literature[key]}")
        return " ".join(f"{i+1}. {item}" for i, item in enumerate(content))

def process_similar_seqs(similar_sequences: list) -> str:
    if len(similar_sequences) > 0:
        content = []
        for s in similar_sequences:
            keys = list(s.keys())
            temp = [f"[{key}]: {s[key]}" for key in keys]
            content.append(" ".join(temp))
        return "\n".join(f"{i+1}. {item}" for i, item in enumerate(content))
    else:
        return None 
def dict2text(peptide_data: dict) -> str:
    text = set()
    properties = list(peptide_data.keys())

    for p in properties:
        if p == "Biological Activity":
            if process_BA(peptide_data[p]) is not None:
                text.add(f"[Biological Activity] {process_BA(peptide_data[p])}")
        elif p == "UniProt Entry":
            if process_UE(peptide_data[p]) is not None:
                text.add(f"[UniProt Entry] {process_UE(peptide_data[p])}")
        elif p == "Literature":
            if process_Literature(peptide_data[p]) is not None:
                text.add(f"[Literature] {process_Literature(peptide_data[p])}")
        elif p == "Similar Sequences":
            if process_similar_seqs(peptide_data[p]) is not None:
                text.add(f"[Similar Sequences]\n {process_similar_seqs(peptide_data[p])}")
        elif p in KEYS_EXIST:
            if isinstance(peptide_data[p], str):
                if flit_str(peptide_data[p]):
                    text.add(f"[{p}] {peptide_data[p]}")
            else:
                text.add(f"[{p}] {peptide_data[p]}")
    return "\n".join(text)

