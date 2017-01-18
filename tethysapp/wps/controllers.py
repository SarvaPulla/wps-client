from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import xml.etree.ElementTree as et
import urllib2
from tethys_sdk.gizmos import SelectInput
from django.http import JsonResponse, HttpResponse
from owslib.wps import WebProcessingService, printInputOutput, monitorExecution, WPSExecution


@login_required()
def home(request):
    """
    Controller for the app home page.
    """
    #Context Variable for saving the data
    data = ''
    #Context List for storing all Capabilities' titles on Web Processing Server
    title = []
    # Context List for storing all Capabilities' identifiers on Web Processing Server
    identifier = []
    number = []
    #Context Variable for storing the user-inputted url. This variable will be used later in hidden divs.
    #This makes it such that the URL can be reusable for multiple requests.
    url = ''

    #Retrieving the POST data to generate a dropdown of all the available processes
    if request.POST and 'wps_url' in request.POST:

        #Variable containing the WPS server URL as specified by the user
        url = request.POST['wps_url']
        #Adding a static string to retrieve getCapabilities
        full_url = url +'/WebProcessingService?Request=GetCapabilities&Service=WPS'

        #Registering a WebProcessingService through the OWSLib module
        wps = WebProcessingService(full_url)

        #Retrieving all the processes available for the requested URL
        wps.getcapabilities()

        #Sorting through the processes and storing the Title and Identifiers in seperate lists
        for process in wps.processes:
            title.append(process.title)
            identifier.append(process.identifier)

    #Combining the title and identifier list so that they can be used in the tethys select gizmo
    options = zip(title,identifier)

    #Tethys Gizmo for generating a dropdown with all the available processes. Identifiers are the option values and the Titles are the display text.
    select_service = SelectInput(display_text='Select a WPS Service',
                                 name='select_service',
                                 multiple=False,
                                 options= options)


    context = {'data':data,'title':title,'url':url,'select_service':select_service}

    return render(request, 'wps/home.html', context)

#Incase someone wants to use a separate controller for handling the getCapabilities. This function is currently not in use.
"""
def getCapabilities(request):

    try:
        json_dict = {"status": "success"}
        processes_list = []
        if request.POST and 'wps_url' in request.POST:
            url = request.POST['wps_url']
            wps_url = url + '/WebProcessingService?Request=GetCapabilities&Service=WPS'
            wps = WebProcessingService(wps_url,verbose=False, skip_caps=True)
            wps.getcapabilities()

            for p in wps.processes:
                process = {}
                process["id"] = p.identifier
                process["title"] = p.title
                processes_list.append(process)
        json_dict["processes"] = processes_list

    except Exception as ex:
        json_dict['status'] = "error"
    finally:
        return JsonResponse(json_dict)
"""

#Controller for generating a dynamic form that will allow execution of a selection process.
def getDescription(request):
    try:
        #Receiving the selected process from the dropdown
        if request.POST and 'select_service' in request.POST:
            #List for storing the input identifiers
            identifier_list = []
            # List for storing the input tiles
            title_list = []
            # List for storing the dictionary that will be used to generate the input boxes for the execute form.
            input_list = []
            #List for storing the dictionary that will be used to display the datatype for the execute form.
            datatype_list = []
            #List for storing the dictionary that will generate the supported formats for the complex datatype in the execute form.
            metadata_list = []
            #List for storing the dictionary that will generate the default format for the complex datatype in the execute form.
            default_list = []
            #List for storing the dictionary that will show the boundingbox datatype default format.
            box_def_list = []
            # List for storing the dictionary that will show the boundingbox datatype supported formats.
            box_sup_list = []

            #The selected process from the getCapabilities dropdown.
            wps_service = request.POST['select_service']

            #Using the hidden url context variable to retrieve this value.
            url = request.POST['hidden_url']
            #The URL for retrieving the describe process xml. Currently, it is static. Once 2.0.0 is more prevelant need to make this segment dynamic.
            full_url = url + '/WebProcessingService?Request=DescribeProcess&SERVICE=WPS&VERSION=1.0.0&identifier=' + wps_service
            #Opening the desribe url
            response = urllib2.urlopen(full_url)
            data = response.read()
            #Converting the xml data to be compatible with the xml etree module
            parse_xml = et.fromstring(data)
            #Parsing through the XML file
            #Retriving all the child nodes in the file
            for child in parse_xml:
                for items in child:
                    get_contents = items.tag
                    # Narrowing down to the DataInputs tag
                    if get_contents.find('DataInputs') != -1:
                        #Going through each of the tags in the DataInputs tag
                        for elements in items:

                            for inputs in elements:
                                get_inputs = inputs.tag
                                # Narrowing down to the Input Identifier tag
                                if get_inputs.find('Identifier') != -1:
                                    #Generating a dictionary to store the inputs
                                    input_generator = {}
                                    identifier = inputs.text
                                    input_generator["id"] = identifier

                                    # Generating a dictionary to store the datatypes
                                    datatype_generator = {}
                                    datatype_generator["id"] = identifier

                                    # Generating a dicitonary to store the default format for the complex datatype
                                    default_generator = {}
                                    default_generator["id"] = identifier

                                    # Generating a dicitonary to store the supported formats for the complex datatype
                                    metadata_generator = {}
                                    metadata_generator["id"] = identifier

                                    # Generating a dicitonary to store the default format for the boundingbox datatype
                                    bbox_default_generator = {}
                                    bbox_default_generator["id"] = identifier

                                    # Generating a dicitonary to store the supported formats for the boundingbox datatype
                                    bbox_support_generator = {}
                                    bbox_support_generator["id"] = identifier

                                    #Storing the identifiers for the inputs in a list
                                    identifier_list.append(identifier)

                                # Narrowing down to the Input Title tag
                                if get_inputs.find('Title') != -1:
                                    #Adding the title as a value to the input_generator dictionary
                                    title = inputs.text
                                    input_generator["title"] = title
                                    #Storing the titles for the inputs in a list
                                    title_list.append(title)

                                #Creating a list for storing all the default formats for the complex datatype
                                default_type_list = []
                                # Creating a list for storing all the supported formats for the complex datatype
                                supported_type_list = []
                                # Creating a list for storing all the supported formats for the boundingbox datatype
                                box_support_list = []
                                # Creating a list for storing all the default formats for the boundingbox datatype
                                box_default_list = []

                                if 'Data' in get_inputs:
                                    # Adding the datatype to the datatype_generator dictionary
                                    datatype_generator["datatype"] = inputs.tag

                                    #Looping through the datatype
                                    for branches in inputs:
                                        values = branches.tag
                                        #Narrowing down to the Default Data tag
                                        if values.find("Default") != -1:
                                            for loop in branches:
                                                box = loop.tag
                                                #Narrowing down to the boundingbox datatype's default format
                                                if box.find('CRS') != -1:
                                                    #Adding the bounding box default formats to the list
                                                    box_default_list.append(loop.text)
                                                for supported in loop:
                                                    info = supported.tag
                                                    # Narrowing to the complex datatype's default format
                                                    if info.find("MimeType") != -1:
                                                        #Adding the complex datatype's default formats to the list
                                                        default_type_list.append(supported.text)
                                        #Entering the Supported tag
                                        if values.find("Supported") != -1:
                                            for loop in branches:
                                                box = loop.tag
                                                #Narrowing to the boundingbox datatype's supported formats
                                                if box.find('CRS') != -1:
                                                    #Adding the boundingbox datatype's supported formats to the list
                                                    box_support_list.append(loop.text)
                                                for supported in loop:
                                                    info = supported.tag
                                                    # Narrowing to the complext datatype's supported formats
                                                    if info.find("MimeType") != -1:
                                                        #Adding the complex datatype's supported formats to the list
                                                        supported_type_list.append(supported.text)

                                    # Adding the newly generated lists to their respective dictionary. This ensures that each list is assigned to a unique Input id
                                    default_generator["defaultTypes"] = default_type_list
                                    metadata_generator["supportedTypes"] = supported_type_list
                                    bbox_default_generator["projection"] = box_default_list
                                    bbox_support_generator["projection"] = box_support_list

                            #Adding all the dictionaries to a list. Each list generates a consolidated dictionary.
                            input_list.append(input_generator)
                            datatype_list.append(datatype_generator)
                            metadata_list.append(metadata_generator)
                            default_list.append(default_generator)
                            box_def_list.append(bbox_default_generator)
                            box_sup_list.append(bbox_support_generator)


            #Creating json objects for storing the dictionaries
            json_dict_input = {"status": "success"}
            json_dict_type = {"status": "success"}
            json_dict_meta = {"status": "success"}
            json_dict_default = {"status": "success"}
            json_dict_boxdef = {"status": "success"}
            json_dict_boxsup = {"status": "success"}

            #Assigning a key,value to each dictionary so that it will be easier to retrieve them via JSON.
            json_dict_input["input"] = input_list
            json_dict_type["type"] = datatype_list
            json_dict_meta["meta"] = metadata_list
            json_dict_default["default"] = default_list
            json_dict_boxdef["boxdef"] = box_def_list
            json_dict_boxsup["boxsup"] = box_sup_list

            # Consolidating all the JSON objects into one JSON object. This JSON object will be returned in the AJAX call. The data can be manipulated as desired.
            one_json = {"status": "success"}
            one_json["input"] = input_list
            one_json["type"] = datatype_list
            one_json["meta"] = metadata_list
            one_json["default"] = default_list
            one_json["boxdef"] = box_def_list
            one_json["boxsup"] = box_sup_list


    except Exception as ex:
        one_json['status'] = "error"
    finally:

        #Returning all the dictionaries as one massive JSON object
        return JsonResponse(one_json)

def getResults(request):
    try:
        #Retriving the URL and the selected process to retrive the execute form data
        if request.POST and 'hidden_service' in request.POST:
            #List for saving the input identifier tags
            identifier_list = []
            #List for saving the output identifier tags
            output_list = []

            #The hidden tags were generated through the AJAX calls in the front end. Now using them to get the names and ids of the dynamic execute form which was generated on the front end.
            wps_service = request.POST['hidden_service']
            url = request.POST['hidden_wps_url']

            full_url = url + '/WebProcessingService?Request=DescribeProcess&SERVICE=WPS&VERSION=1.0.0&identifier=' + wps_service
            response = urllib2.urlopen(full_url)
            data = response.read()
            parse_xml = et.fromstring(data)
            for child in parse_xml:
                for items in child:
                    get_contents = items.tag
                    if get_contents.find('DataInputs') != -1:
                        for elements in items:
                            for inputs in elements:
                                get_inputs = inputs.tag
                                # print get_inputs
                                if get_inputs.find('Identifier') != -1:
                                    identifier = inputs.text
                                    identifier_list.append(identifier)
                    if get_contents.find('ProcessOutputs') != -1:
                        for elements in items:
                            for outputs in elements:
                                get_outputs = outputs.tag
                                if get_outputs.find('Identifier') != -1:
                                    identifier = outputs.text
                                    output_list.append(identifier)

            execute_functions = []
            for name in identifier_list:
                value = request.POST[name]
                str = "{0}={1}".format(name, value)
                execute_functions.append(str)
            data_inputs =  ';'.join(execute_functions)
            data_outputs = ';'.join(output_list)
            execute_url = url + '/WebProcessingService?request=Execute&service=WPS&version=1.0.0&Identifier=' + wps_service+'&DataInputs='+data_inputs+'&ResponseDocument='+data_outputs+'&StoreExecuteResponse=true'
            wps_url = url + '/WebProcessingService?Request=GetCapabilities&Service=WPS'
            wps = WebProcessingService(wps_url, verbose=False, skip_caps=True)
            wps.getcapabilities()

            one_json = {"status": "success"}
            one_json["id"] = identifier_list
            one_json["url"] = execute_url


    except Exception as ex:
        one_json['status'] = "error"
    finally:
        return JsonResponse(one_json)

def getXML(request):
    if request.POST and 'hidden_xml_url' in request.POST:

        url = request.POST['hidden_xml_url']
        response = urllib2.urlopen(url)
        data = response.read()
        parse_xml = et.fromstring(data)
        for child in parse_xml:
            print child.tag
            # for items in child:
            #     get_contents = items.tag
        xml_response = HttpResponse(data,content_type='text/xml')
        xml_response['Content-Disposition'] = "attachment; filename=output.xml"

    return xml_response

