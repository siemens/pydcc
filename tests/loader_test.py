import dcc.dcc_xml_validator as vali


if __name__ == "__main__":

    myvali = vali.DCCXMLValidator()

    myvali.download_list_with_avalable_releases()

    myvali.download_schemas()

    myvali.download_dependencys()

    #print(myvali.data)
