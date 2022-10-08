from re import findall
import bs4
from bs4 import BeautifulSoup
import datetime
from dateutil.parser import parse


print("what")

class Francise :
    """
    class representing francise
    """

    def __init__(
        self,
        name:str = "",
        business_sign:str = "",
        representatives:list = [],
        business_type:str = "",
        corporate_registration_date:datetime.datetime = "",
        business_registration_date:datetime.datetime = "",
        key_number:str = "",
        key_fax_number:str = "",
        registration_id:str = "",
        initial_registration_date:datetime.datetime = "",
        final_registration_date:datetime.datetime = "",
        url:str = None
    ) -> None:
        """
        
        dictionary로 사용하기는 value들을 string인 key로 접근하기 불편해서 class로 만들었습니다.

        args :

            name : str
                상호
                default : ""
            business_sign : str
                영업 표지
                default : ""
            representatives : list
                대표자.  여럿일 수 있음.
                default : []
            business_type : str
                업종
                default : ""
            corporate_registration_date : datetime.datetime
                법인설립등기일
                default : ""
            business_registration_date : datetime.datetime
                사업자등록일
                default : ""
            key_number : str
                대표번호
                default : ""
            key_fax_number : str
                default : ""
                대표팩스 번호
            registration_id : str
                등록번호
                default : ""
            initial_registration_date : datetime.datetime
                최초등록일
                default : ""
            final_registration_date : datetime.datetime
                최종등록일
                default : ""
                 
        # ㅇㅜㅣㅇㅡㅣ ㅈㅓㅇㅂㅗㄷㅡㄹ 말고도 제공하는 정보가 굉장히 많은데,
        # ㅇㅏㅈㅣㄱ ㅊㅓㄹㅣㅎㅏㅈㅣ ㅁㅗㅅㅎㅐㅆㅅㅡㅂㄴㅣㄷㅏ.
            url : None
                url of site.
                if provided, call self.parseFromUrl
                to parse data from html and save into instance variable
        
        """
        self.name = name
        self.sign = business_sign
        self.representatives = representatives
        self.type = business_type
        self.corporate_registration_date = corporate_registration_date
        self.business_registration_date = business_registration_date
        self.key_number = key_number
        self.key_fax_number = key_fax_number
        self.registration_id = registration_id
        self.initial_registration_date = initial_registration_date
        self.final_registration_date = final_registration_date

        if url is not None :
            self.parseFromUrl(url)        

    def parseFromUrl(self, url) :
        """
        
        args : 
            url :

        return :
            None
        """
        soup = BeautifulSoup(url, "lxml")
        
        self.parseGeneralCurrentCondition(soup.form.find("div", "box_flop").table)




    def parseGeneralCurrentCondition(
        self,
        general_curr_state_table_tag : bs4.element.Tag
    ) -> None :
        """
        input part html tag containig information of "가맹본부 일반 현황",
        and parse information

        args : bs4.element.Tag
            general_curr_state_table_tag

        return :
            None
        """

        table_rows = general_curr_state_table_tag.tbody.findAll('tr')

        business_name, business_sign, representative, business_type = list(map(
            lambda table_data : table_data.text.strip().replace("\t", '').split("\n")[-1],
            table_rows[0].findAll("td")
        ))
        representative = representative.split(",")

        corporate_registration_date, business_registration_date, key_number, key_fax_number = list(map(
            lambda table_data : table_data.text.strip().replace(" ", "").replace("\xa0",""),
            table_rows[2].findAll("td")
        ))
        corporate_registration_date = parse(corporate_registration_date)
        business_registration_date = parse(business_registration_date)

        registration_id, initial_registration_date, final_registration_date, _ = list(map(
            lambda table_data : table_data.text.strip(),
            table_rows[4].findAll("td")
        ))
        initial_registration_date = parse(initial_registration_date)
        final_registration_date = parse(final_registration_date)

        self.name = business_name
        self.sign = business_sign
        self.representatives = representative
        self.type = business_type
        self.corporate_registration_date = corporate_registration_date
        self.business_registration_date = business_registration_date
        self.key_number = key_number
        self.key_fax_number = key_fax_number
        self.registration_id = registration_id
        self.initial_registration_date = initial_registration_date
        self.final_registration_date = final_registration_date