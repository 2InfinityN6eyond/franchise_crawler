from re import findall
import bs4
from bs4 import BeautifulSoup
import datetime
from dateutil.parser import parse

class Franchise :
    """
    가맹본부에 해당하는 class이다.
    
    2022-10-9 기준, 가맹사업정보제공시스템의 정보공개서 웹 페이지에서 
    ex)
    https://franchise.ftc.go.kr/mnu/00013/program/userRqst/view.do?firMstSn=133332
    "가맹본부의 일반 현황" 에 포함되는 데이터만을 저장할 수 있다.
    또한, 가맹본부의 데이터가 변경될 경우, 단순히 이전 데이터에 덮어써야 한다.
    """

    def __init__(
        self,
        num:str = "",
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
            num : str
                가맹사업정보제공시스템의 가맹본부의 리스트를 보여주는 웹페이지에서,
                table 로 정보를 보여줄 때, '번호' 열에 해당하는 데이터
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
                 
        # 위의 정보 말고도 말고도 제공하는 정보가 굉장히 많은데,
        # 아직 그것들을 반영할 수 있는 데이터베이스의 스키마를 설계하지 못했습니다.
            url : None
                url of site.
        """
        self.num = num
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
        
        self.url = url
        self.parsing_succeed = False

    def parseFromHtml(self, html_text:str) -> None :
        """
        가맹사업정보제공시스템에서 특정 가뱅본부의 정보를 공개하는 웹페이지에 해당하는 url을 입력받아
        웹 페이지에 공개된 정보들을 파싱해 해당하는 instance variable에 저장한다.

        args : 
            html_text : str
                특정 가맹본부의 정보를 공개하는 웹페이지 (view_url) 의 html 텍스트

        return : None
        """


        soup = BeautifulSoup(html_text, "lxml")

        try :
            # 각 프렌차이즈의 정보를 공개하는 웹페이지의 html에서 
            # 웹페이지의 "가맹본부 일반 현황" 에 해당하는 부분을 파싱한다.
            self.parseGeneralCurrentCondition(soup.form.find("div", "box_flop").table)

            # 다른 정보들을 파싱하는 부분도 만들어야 함..
            pass

        except Exception as e :
            print("failed to parse html from view_url {}".format(
                self.url
            ))
            print("message :")
            print(e)

            self.parsing_succeed = False


    def parseGeneralCurrentCondition(
        self,
        general_curr_state_table_tag : bs4.element.Tag
    ) -> None :
        """
        가맹사업정보제공시스템에서 특정 가맹본부의 정보를 공개하는 웹페이지의 html 중
        웹페이지에서 "가맹본부 일반 현황" 에 해당하는 부분의 태그를 받고,
        "가맹본부 일반 현황" 에 해당하는 정보들을 파싱해 해당하는 instance variable에 저장한다.

        args : bs4.element.Tag
            general_curr_state_table_tag

        return :
            None
        """

        try :
                
            # argument로 전달된 table태그에서 table body를 추출하고,
            # 그 안에서 모든 table_row를 찾는다. 
            table_rows = general_curr_state_table_tag.tbody.findAll('tr')

            # 테이블이 깔끔하지 않게 만들어져 있어 파싱하는 부분도 깔끔하지 못함.

            # 테이블의 첫번쨰 열에서 [상호, 영업표지, 대표자, 업종] 을 파싱함
            business_name, business_sign, representative, business_type = list(map(
                # 첫번째 열은 조금 html이 조금 이상하게 구성되어 있음. 처리해주어야 함.
                lambda table_data : table_data.text.strip().replace("\t", '').split("\n")[-1],
                table_rows[0].findAll("td")
            ))
            # 대표자는 여러명일 수도 있기 때문에 list로 저장
            representative = representative.split(",") 

            # 세번쨰 열에서 [법인설립등기일, 사업자등록일, 대표번호, 대표팩스번호] 를 파싱함
            corporate_registration_date, business_registration_date, key_number, key_fax_number = list(map(
                # 전화번호 데이터에 이상한 특수기호가 포함되어 있어서 처리해주어야 함.
                lambda table_data : table_data.text.strip().replace(" ", "").replace("\xa0",""),
                table_rows[2].findAll("td")
            ))
            # 날짜데이터는 datetime.datetime 타입으로 파싱함
            #corporate_registration_date = parse(corporate_registration_date)
            #business_registration_date = parse(business_registration_date)

            # 다섯번쨰 열에서 [등록번호, 최초등록일, 최종등록일] 을 파싱함.
            registration_id, initial_registration_date, final_registration_date, _ = list(map(
                lambda table_data : table_data.text.strip(),
                table_rows[4].findAll("td")
            ))
            # 날짜데이터는 datetime.datetime 타입으로 파싱함
            #initial_registration_date = parse(initial_registration_date)
            #final_registration_date = parse(final_registration_date)

            # 파싱한 데이터를 해당하는 instance variable 에 저장
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
        
            # url이 잘못돼 템플릿 웹페이지에 들어가도 파싱 과정에서 에러가 발생하지 않는 경우가 있다.
            # 그 경우에 대비해 Exception을 발생시킨다.
            if 0 in [ # 만약 파싱한 값 중에 빈 값이 있다면, Exception을 발생시킨다.
                len(self.name),
                len(self.sign),
                len(self.representatives),
                len(self.type),
                len(self.corporate_registration_date),
                len(self.business_registration_date),
                len(self.key_number),
                len(self.key_fax_number),
                len(self.registration_id),
                len(self.initial_registration_date),
                len(self.final_registration_date),
            ] :
                raise Exception

            self.parsing_succeed = True

        except Exception as e :
            self.parsing_succeed = False

    def __str__(self) -> str:
        return "파싱_성공:{0}, 번호:{1:4s}, 등록번호:{2:11s}, 상호:{3}, 영업 표지:{4}\n".format(
            'T' if self.parsing_succeed else 'F',
            self.num, self.registration_id, self.name, self.sign
        )

    def __repr__(self) -> str:
        return self.__str__()